import streamlit as st
import os
import base64
import io
import re
import platform
from pathlib import Path
from pdf2image import convert_from_bytes
from dashscope import MultiModalConversation, Generation
import dashscope
from http import HTTPStatus
import zipfile
import requests
import shutil

POPPLER_DOWNLOAD_URL = "https://github.com/oschwartz10612/poppler-windows/releases/download/v25.12.0-0/Release-25.12.0-0.zip"

# ================= 页面配置 =================
st.set_page_config(
    page_title="PDF2MD",
    page_icon="📃",
    layout="wide"
)

# ================= 工具函数 =================
def ensure_poppler_exists():
    """自动化环境检查与下载 (仅限 Windows)"""
    if platform.system() != "Windows":
        return
        
    base_dir = Path(__file__).parent
    poppler_dir = base_dir / "poppler"
    
    # 如果 poppler 文件夹已经存在且内部结构正确，直接返回
    if poppler_dir.exists() and (poppler_dir / "Library" / "bin").exists():
        return
        
    st.warning("🚀 正在为您自动配置 PDF 处理引擎 (Poppler)，这可能需要 1-2 分钟...")
    
    try:
        # 1. 清理可能存在的残余
        zip_path = base_dir / "poppler_temp.zip"
        if zip_path.exists(): os.remove(zip_path)
        
        # 2. 下载压缩包
        with st.spinner("正在从 GitHub 下载组件..."):
            response = requests.get(POPPLER_DOWNLOAD_URL, stream=True, timeout=60)
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
        # 3. 解压
        with st.spinner("正在解压并重组目录..."):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(base_dir)
            
            # --- 智能寻找解压后的目录 ---
            # 遍历当前目录，寻找那个包含 'Library' 的新文件夹
            found_folder = None
            for p in base_dir.iterdir():
                if p.is_dir() and (p / "Library").exists() and p.name != "poppler":
                    found_folder = p
                    break
            
            if found_folder:
                # 如果已存在名为 poppler 的旧文件夹，先改名或删除
                if poppler_dir.exists():
                    shutil.rmtree(poppler_dir)
                # 将找到的文件夹重命名为 poppler
                found_folder.rename(poppler_dir)
            else:
                # 如果没找到(可能是扁平解压)，尝试建立 poppler 目录
                st.error("无法识别解压后的目录结构，请手动检查。")
                
        # 4. 最终清理
        if zip_path.exists(): os.remove(zip_path)
        st.success("✅ 环境配置成功！正在继续...")
        st.rerun() # 强制刷新一次以应用新路径

    except Exception as e:
        st.error(f"❌ 自动配置失败: {str(e)}")
        st.info("建议手动下载并解压到项目根目录下的 poppler 文件夹中。")
        st.stop()


def get_poppler_path():
    """获取 Poppler 路径"""
    if platform.system() == "Windows":
        ensure_poppler_exists()
        # 最终路径锁定在 poppler/Library/bin
        poppler_bin = Path(__file__).parent / "poppler" / "Library" / "bin"
        return str(poppler_bin) if poppler_bin.exists() else None
    return None


def encode_image_to_base64(image):
    """将 PIL 图片对象转换为 Base64 字符串"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{img_str}"

def clean_markdown_shell(text):
    """去除 Markdown 代码块包裹壳子"""
    if not text:
        return ""
    text = re.sub(r'^```(markdown|json)?\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\n```$', '', text)
    return text.strip()

# --- 阶段二：单页清洗 ---
def call_page_level_optimization(raw_text, model_name):
    prompt = (
        "你是一个OCR后处理专家。下文是单页文档的OCR结果。请修复Markdown格式错误（如未闭合的表格、加粗符号），"
        "去除页眉页脚（如'Page 1'），但严禁修改原文数值和内容。直接输出修复后的Markdown。"
        "特别注意：去除所有疑似水印的文字内容。"
    )
    messages = [{'role': 'user', 'content': f"{prompt}\n\n原始文本：\n{raw_text}"}]
    try:
        response = Generation.call(model=model_name, messages=messages, result_format='message')
        if response.status_code == HTTPStatus.OK:
            return response.output.choices[0].message.content
        return raw_text 
    except:
        return raw_text

# --- 阶段三：全局重组 ---
def call_global_refinement(full_text, model_name):
    prompt = (
        "你是一个专业的文档出版编辑。下文是由多页OCR结果拼接成的Markdown文档，可能存在标题层级混乱、跨页段落断裂等问题。\n"
        "你的任务是进行【全局重构】：\n"
        "1. **统一标题层级**：根据上下文，确保 '一、'、'1.'、'(1)' 等序号的层级关系在全文中是连续且统一的。\n"
        "2. **合并跨页段落**：如果前一页的结尾和后一页的开头明显是同一句话，请将它们合并，删除中间的换行。\n"
        "3. **统一表格风格**：确保所有表格的格式一致。\n"
        "4. **语义理解**：根据读取到的内容，自动在合适的地方加入加粗、下划线，并将数学公式还原为标准 Latex。\n"
        "5. **标点统一**：如果中文内容占比大，请将符号统一为中文全角标点；如果英文内容占比大，请使用半角标点。\n"
        "6. **内容限制**：只修改格式，严禁生成任何额外内容。如果内容是试卷，即使有询问也不要给出答案，只输出试卷文本本身。\n"
        "7. **智能标注**：阅读所有文本，理解文档层级关系，并利用markdown语法加入合适大纲级别，如'# 一、选择题' \n"
        "8. **缩进管理**：确保排版后的文本具有极为规范的缩进关系，如试卷的选项均应对齐\n"
        "8. **直接输出**：只输出优化后的Markdown全文，禁止输出任何代码块标记（如 ```markdown）或解释性废话。\n\n"
        "文档全文如下：\n"
        f"{full_text}"
    )
    
    messages = [{'role': 'user', 'content': prompt}]
    try:
        response = Generation.call(
            model=model_name,
            messages=messages,
            result_format='message'
        )
        
        if response.status_code == HTTPStatus.OK:
            if hasattr(response, 'output') and response.output.choices:
                return response.output.choices[0].message.content
            return "⚠️ [错误] API返回成功但内容为空"
        else:
            return f"❌ [API错误] 状态码: {response.status_code}, 信息: {response.message}"
    except Exception as e:
        return f"❌ [系统异常] 全局重组崩溃: {str(e)}"

# ================= 侧边栏配置 =================
with st.sidebar:
    st.header("⚙️ 引擎配置")
    st.markdown("[🔗 阿里云模型列表](https://help.aliyun.com/zh/model-studio/getting-started/models)")
    st.markdown("[🔗 百炼API](https://bailian.console.aliyun.com/tab=model#/api-key)")

    user_api_key = st.text_input("阿里云 API Key", type="password", placeholder="sk-...")
    
    st.divider()
    
    st.subheader("OCR 识别")
    ocr_model = st.selectbox("视觉模型", ["qwen-vl-ocr", "qwen-vl-ocr-latest", "qwen-vl-max-latest"], index=1)

    st.divider()

    st.subheader("单页清洗")
    enable_page_clean = st.checkbox("开启单页修复", value=True, help="修复每页的表格闭合、水印和乱码")
    clean_model = "qwen-plus"

    st.divider()

    st.subheader("全局重组")
    enable_global_refine = st.checkbox("开启全文重组 (推荐)", value=True, help="统一调整全文标题序号、合并跨页段落及标点")
    
    if enable_global_refine:
        global_model = st.selectbox(
            "重组模型", 
            ["qwen-plus", "qwen-max", "qwen-long", "qwen-flash"], 
            index=0,
            help="建议使用qwen-plus，长文档使用qwen-long"
        )
    
    st.info(f"当前运行系统: {platform.system()}")

# ================= 主界面 =================
st.title("PDF to Markdown Converter")
st.subheader("Powered by Qwen")
st.markdown("流程：`视觉识别` ➔ `单页修复` ➔ `全局重组`")

uploaded_file = st.file_uploader("📂 拖入 PDF 文件", type=["pdf"])

if uploaded_file and user_api_key:
    dashscope.api_key = user_api_key
    p_path = get_poppler_path()
    
    # Windows 环境特有的检查
    if p_path == "MISSING":
        st.error("❌ Windows 运行错误：未在项目根目录下找到 `poppler` 文件夹！")
        st.info("请确保 poppler 文件夹与 app.py 在同一目录下。")
        st.stop()

    if st.button("开始全流程处理", type="primary"):
        status_container = st.container()
        progress_bar = st.progress(0)
        intermediate_pages = []
        
        try:
            # 1. 预处理
            status_container.info("⏳ 正在读取 PDF 并转换为图片流...")
            pdf_bytes = uploaded_file.read()
            
            # 智能传入 poppler_path
            # Windows 会传入路径字符串，macOS/Linux 会传入 None
            images = convert_from_bytes(pdf_bytes, dpi=200, poppler_path=p_path)
            total_pages = len(images)
            
            # 2. 逐页循环 (阶段一 & 阶段二)
            for i, img in enumerate(images):
                page_num = i + 1
                
                # --- Stage 1: OCR ---
                status_container.write(f"🔵 [Page {page_num}/{total_pages}] 视觉识别中...")
                img_base64 = encode_image_to_base64(img)
                messages = [{"role": "user", "content": [{"image": img_base64}, {"text": "提取文字并保持Markdown格式，直接输出内容，不要废话。"}]}]
                
                ocr_resp = MultiModalConversation.call(model=ocr_model, messages=messages)
                if ocr_resp.status_code != 200:
                    st.error(f"第 {page_num} 页 OCR 识别失败: {ocr_resp.message}")
                    continue
                page_text = ocr_resp.output.choices[0].message.content[0]['text']
                
                # --- Stage 2: Page Clean ---
                if enable_page_clean:
                    status_container.write(f"🟢 [Page {page_num}/{total_pages}] 正在修复格式与去水印...")
                    page_text = call_page_level_optimization(page_text, clean_model)
                    page_text = clean_markdown_shell(page_text)
                
                intermediate_pages.append(page_text)
                
                # 更新进度 (保留最后 10% 给全局重组)
                progress_bar.progress(int((page_num / total_pages) * 90))

            # 3. 全局合并 (阶段三)
            full_raw_text = "\n\n".join(intermediate_pages)
            final_output_text = full_raw_text

            if enable_global_refine:
                status_container.warning(f"🟠 [Global] 正在统筹全文逻辑、优化标点与合并跨页内容...")
                progress_bar.progress(95)
                
                refined_text = call_global_refinement(full_raw_text, global_model)
                # 再次清洗，确保没有代码块壳子
                final_output_text = clean_markdown_shell(refined_text)
            
            progress_bar.progress(100)
            status_container.success("✅ 全流程处理完毕！")
            
            # 4. 结果展示
            tab1, tab2 = st.tabs(["✨ 最终结果", "📄 中间原始数据"])
            
            with tab1:
                col_left, col_right = st.columns([4, 1])
                with col_right:
                    st.download_button(
                        "📥 点击下载 Markdown", 
                        final_output_text, 
                        file_name=f"{uploaded_file.name.split('.')[0]}_AI_Cleaned.md",
                        use_container_width=True
                    )
                st.markdown(final_output_text)
            
            with tab2:
                st.text_area("OCR 原始拼接内容 (未经过全局重组)", full_raw_text, height=500)

        except Exception as e:
            st.error(f"❌ 运行异常: {str(e)}")
            if "poppler" in str(e).lower():
                st.info("💡 提示：如果是 macOS，请确保已运行 `brew install poppler`。")

elif uploaded_file and not user_api_key:
    st.warning("👈 请先在侧边栏输入您的阿里云 API Key")