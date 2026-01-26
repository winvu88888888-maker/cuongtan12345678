import streamlit as st
import sys
import os
import json
import importlib.util
from pathlib import Path
from datetime import datetime

# --- SYSTEM DIAGNOSTICS & PATH SETUP ---
def setup_environment():
    """Setup paths and return basic info for debugging if needed."""
    try:
        # 1. Get current file and dir
        this_file = os.path.abspath(__file__)
        this_dir = os.path.dirname(this_file)
        # 2. Get root dir (parent of web/)
        root_dir = os.path.dirname(this_dir)
        
        # 3. Add to path
        if root_dir not in sys.path:
            sys.path.insert(0, root_dir)
        if this_dir not in sys.path:
            sys.path.insert(0, this_dir)
            
        return {
            "this_file": this_file,
            "this_dir": this_dir,
            "root_dir": root_dir,
            "sys_path": sys.path[:5] # First 5 for brevity
        }
    except Exception as e:
        return {"error": str(e)}

ENV_INFO = setup_environment()

# --- DEFINE FALLBACK FUNCTIONS ---
def render_universal_data_hub_tab(): 
    st.error("⚠️ Lỗi Tải Tab: Không tìm thấy module `ai_factory_tabs`.")
    if st.checkbox("Hiển thị thông tin chẩn đoán"):
        st.json(ENV_INFO)
def render_system_management_tab(): st.error("Lỗi Tab Quản trị")
def add_to_hub(*args, **kwargs): return False

# --- ULTRA-ROBUST DYNAMIC IMPORT ---
def load_factory_tabs():
    global render_universal_data_hub_tab, render_system_management_tab, add_to_hub
    
    # List of import patterns to try
    targets = [
        "web.ai_factory_tabs",        # Pattern A: Package-based
        "ai_factory_tabs",            # Pattern B: Direct-based
    ]
    
    # Try standard imports first
    for target in targets:
        try:
            mod = importlib.import_module(target)
            render_universal_data_hub_tab = mod.render_universal_data_hub_tab
            render_system_management_tab = mod.render_system_management_tab
            add_to_hub = mod.add_to_hub
            return True # Success
        except ImportError:
            continue
            
    # Pattern C: Absolute File Path (The ultimate weapon)
    try:
        if "this_dir" in ENV_INFO:
            target_path = os.path.join(ENV_INFO["this_dir"], "ai_factory_tabs.py")
            if os.path.exists(target_path):
                spec = importlib.util.spec_from_file_location("ai_factory_tabs_fixed", target_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                render_universal_data_hub_tab = mod.render_universal_data_hub_tab
                render_system_management_tab = mod.render_system_management_tab
                add_to_hub = mod.add_to_hub
                return True
    except Exception as e:
        st.warning(f"Lỗi nạp trực tiếp file: {e}")
        
    return False

# Execute loader
if not load_factory_tabs():
    st.sidebar.error("🚨 Lỗi: Không thể nạp `ai_factory_tabs`")

# --- OTHER IMPORTS ---
try:
    from ai_modules.orchestrator import AIOrchestrator
    from ai_modules.memory_system import MemorySystem
except ImportError:
    st.error("⚠️ Không thể tải ai_modules")

# n8n Integration (Fallback logic)
try:
    from n8n_integration import N8nClient as N8NClient, setup_n8n_config
except ImportError:
    class N8NClient:
        def __init__(self, base_url="http://localhost:5678", api_key=None):
            self.base_url = base_url
            self.api_key = api_key
        def test_connection(self): return False
        def get_workflow_statistics(self): return {'total_workflows': 0, 'active_workflows': 0}
        def get_execution_statistics(self): return {'total_executions': 0, 'successful': 0, 'executions': []}
        def get_workflows(self): return []
    def setup_n8n_config(*args, **kwargs): pass

def render_ai_factory_view():
    st.markdown("## 🏭 NHÀ MÁY AI - PHÁT TRIỂN TỰ ĐỘNG")
    st.info("Hệ thống tích hợp n8n: Kỳ Môn Độn Giáp định hướng chiến lược & Gemini AI thực thi kỹ thuật.")
    
    if 'orchestrator' not in st.session_state:
        if 'gemini_key' in st.session_state and st.session_state.gemini_key:
            st.session_state.orchestrator = AIOrchestrator(st.session_state.gemini_key)
        else:
            st.session_state.orchestrator = None
            
    if 'memory' not in st.session_state:
        st.session_state.memory = MemorySystem()
        
    if 'n8n_client' not in st.session_state:
        n8n_url = st.secrets.get("N8N_BASE_URL", "http://localhost:5678")
        n8n_key = st.secrets.get("N8N_API_KEY", None)
        st.session_state.n8n_client = N8NClient(n8n_url, n8n_key)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Dashboard", "✍️ Tạo Code & Dự Án", "📚 Knowledge Base", 
        "🌐 Kho Dữ Liệu Vô Tận", "⚙️ Workflows", "🛠️ Quản Trị Hệ Thống"
    ])

    with tab1: render_dashboard_tab()
    with tab2: render_create_code_tab()
    with tab3: render_knowledge_base_tab()
    with tab4: render_universal_data_hub_tab()
    with tab5: render_workflows_tab()
    with tab6: render_system_management_tab()

def render_dashboard_tab():
    st.subheader("Thống Kê Hoạt Động")
    stats = st.session_state.memory.get_statistics()
    col1, col2, col3, col4 = st.columns(4)
    s = 'padding:15px;border-radius:10px;border-left:5px solid '
    col1.markdown(f'<div style="{s}#667eea;background:#f8f9fa"><h3>📁 {stats.get("total_code_files", 0)}</h3><p>Files Code</p></div>', unsafe_allow_html=True)
    col2.markdown(f'<div style="{s}#764ba2;background:#f8f9fa"><h3>📚 {stats.get("total_knowledge", 0)}</h3><p>Kiến thức</p></div>', unsafe_allow_html=True)
    col3.markdown(f'<div style="{s}#2ecc71;background:#f8f9fa"><h3>⚡ {stats.get("total_executions", 0)}</h3><p>Lần chạy</p></div>', unsafe_allow_html=True)
    success = stats.get("executions_by_status", {}).get("success", 0)
    total = stats.get("total_executions", 1)
    col4.markdown(f'<div style="{s}#e74c3c;background:#f8f9fa"><h3>✅ {int(success/max(1,total)*100)}%</h3><p>Thành công</p></div>', unsafe_allow_html=True)

def render_create_code_tab():
    if st.session_state.orchestrator is None:
        st.warning("⚠️ Vui lòng nhập Gemini API key ở Sidebar.")
        return
    if 'last_res' not in st.session_state: st.session_state.last_res = None

    with st.form("gen_form"):
        req = st.text_area("Mô tả phần mềm của bạn:", height=100)
        if st.form_submit_button("🚀 Bắt Đầu"):
            with st.spinner("🤖 AI đang làm việc..."):
                try:
                    res = st.session_state.orchestrator.process_request(req)
                    nm = res.get('plan',{}).get('project_name','Project')
                    add_to_hub(f"Kế hoạch: {nm}", f"Yêu cầu từ người dùng: {req}", "Nghiên Cứu")
                    for f in res.get('execution',{}).get('created_files',[]):
                        if os.path.exists(f):
                            add_to_hub(f"File: {os.path.basename(f)}", f"```python\n{open(f,'r',encoding='utf-8').read()}\n```", "Mã Nguồn")
                    st.session_state.last_res = res
                    st.rerun()
                except Exception as e: st.error(f"Lỗi: {e}")

    if st.session_state.last_res:
        res = st.session_state.last_res
        st.success("✅ Đã hoàn tất và tự động lưu trữ vào Kho Vô Tận!")
        if res.get('package') and os.path.exists(res['package']):
            st.download_button("📥 Tải Project (.zip)", open(res['package'],"rb"), file_name=os.path.basename(res['package']))
        for f in res.get('execution',{}).get('created_files',[]):
            if os.path.exists(f):
                with st.expander(f"📄 {os.path.basename(f)}"): st.code(open(f, 'r', encoding='utf-8').read())

def render_knowledge_base_tab():
    q = st.text_input("🔍 Tìm kiếm tri thức:")
    if q:
        for i in st.session_state.memory.search_knowledge(q):
            with st.expander(i['topic']): st.markdown(i['content'])

def render_workflows_tab():
    c = st.session_state.n8n_client
    if c.test_connection(): st.success(f"✅ Đã kết nối n8n: {c.base_url}")
    else: st.warning("⚠️ Chưa kết nối n8n server")
