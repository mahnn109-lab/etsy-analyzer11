import streamlit as st
import pandas as pd
import os
import sys
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import random

# 页面配置
st.set_page_config(
    page_title="竞品分析器",
    page_icon="🔍",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stats-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stat-item {
        font-size: 1.1rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# 模拟数据生成函数
def generate_mock_data(keyword, count=12):
    """生成模拟数据用于演示"""
    mock_products = []
    base_prices = [19.99, 24.99, 29.99, 34.99, 39.99, 44.99, 49.99, 54.99, 59.99]
    
    for i in range(count):
        price = random.choice(base_prices) + random.uniform(-5, 5)
        mock_products.append({
            'title': f'{keyword} 商品 #{i+1}',
            'price': round(price, 2),
            'currency': 'USD',
            'image_url': f'https://via.placeholder.com/300x300.png?text=Product+{i+1}',
            'product_url': f'https://www.etsy.com/listing/{random.randint(100000, 999999)}'
        })
    
    return mock_products

# 安装 Playwright 浏览器驱动
@st.cache_resource
def install_playwright():
    """首次运行时安装 Playwright 浏览器"""
    try:
        os.system('playwright install chromium')
        return True
    except Exception as e:
        st.error(f"安装浏览器驱动失败: {str(e)}")
        return False

# Etsy 抓取函数
def scrape_etsy(keyword, max_results=12):
    """
    抓取 Etsy 商品信息
    
    Args:
        keyword: 搜索关键词
        max_results: 最大抓取数量
    
    Returns:
        list: 商品信息列表
    """
    products = []
    use_mock = False
    
    try:
        with sync_playwright() as p:
            # 启动浏览器 - 云端优化配置
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions'
                ]
            )
            
            # 创建上下文 - 伪装真实用户
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US'
            )
            
            page = context.new_page()
            
            # 构建搜索 URL
            search_url = f'https://www.etsy.com/search?q={keyword.replace(" ", "+")}'
            
            # 访问页面
            page.goto(search_url, timeout=30000, wait_until='domcontentloaded')
            
            # 随机等待，模拟人类行为
            time.sleep(random.uniform(2, 4))
            
            # 检查是否被屏蔽
            if 'captcha' in page.url.lower() or 'blocked' in page.content().lower():
                raise Exception("检测到访问限制")
            
            # 等待商品列表加载
            try:
                page.wait_for_selector('[data-search-results-container]', timeout=10000)
            except:
                # 如果无法找到容器，尝试其他选择器
                page.wait_for_selector('.wt-grid', timeout=10000)
            
            # 滚动页面加载更多内容
            for _ in range(3):
                page.evaluate('window.scrollBy(0, 800)')
                time.sleep(1)
            
            # 抓取商品信息 - 使用多个选择器策略
            items = page.query_selector_all('div[data-appears-component-name*="listing"]')
            
            if not items:
                # 备用选择器
                items = page.query_selector_all('.wt-grid__item-xs-6')
            
            for item in items[:max_results]:
                try:
                    # 提取标题
                    title_elem = item.query_selector('h3, h2, .wt-text-caption')
                    title = title_elem.inner_text().strip() if title_elem else 'N/A'
                    
                    # 提取价格
                    price_elem = item.query_selector('.currency-value, [class*="price"]')
                    price_text = price_elem.inner_text().strip() if price_elem else '0'
                    
                    # 清理价格文本
                    price = float(''.join(filter(lambda x: x.isdigit() or x == '.', price_text)))
                    
                    # 提取货币符号
                    currency_elem = item.query_selector('.currency-symbol')
                    currency = currency_elem.inner_text().strip() if currency_elem else 'USD'
                    
                    # 提取图片
                    img_elem = item.query_selector('img')
                    image_url = img_elem.get_attribute('src') if img_elem else ''
                    
                    # 提取链接
                    link_elem = item.query_selector('a')
                    product_url = link_elem.get_attribute('href') if link_elem else ''
                    if product_url and not product_url.startswith('http'):
                        product_url = 'https://www.etsy.com' + product_url
                    
                    products.append({
                        'title': title,
                        'price': price,
                        'currency': currency,
                        'image_url': image_url,
                        'product_url': product_url
                    })
                    
                except Exception as e:
                    continue
            
            browser.close()
            
            # 如果没有抓取到数据，使用模拟数据
            if len(products) == 0:
                use_mock = True
                products = generate_mock_data(keyword, max_results)
                
    except Exception as e:
        st.warning(f"⚠️ 抓取遇到问题: {str(e)}")
        use_mock = True
        products = generate_mock_data(keyword, max_results)
    
    return products, use_mock

# 主程序
def main():
    # 标题
    st.markdown('<div class="main-header">🔍 Etsy 竞品分析器</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">输入关键词，一键分析 Etsy 市场竞品数据</div>', unsafe_allow_html=True)
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置选项")
        keyword = st.text_input("搜索关键词", value="handmade jewelry", help="输入您想要分析的商品关键词")
        max_results = st.slider("抓取数量", min_value=6, max_value=24, value=12, step=6)
        
        analyze_button = st.button("🚀 开始分析", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 📌 使用说明")
        st.markdown("""
        1. 输入商品关键词
        2. 选择抓取数量
        3. 点击开始分析
        4. 查看价格统计和商品列表
        """)
    
    # 分析逻辑
    if analyze_button:
        if not keyword:
            st.error("❌ 请输入搜索关键词")
            return
        
        # 安装浏览器驱动（首次运行）
        with st.spinner("🔧 初始化浏览器环境..."):
            install_playwright()
        
        # 开始抓取
        with st.spinner(f"🔍 正在分析 '{keyword}' 的竞品数据..."):
            products, is_mock = scrape_etsy(keyword, max_results)
        
        if not products:
            st.error("❌ 未能获取到商品数据，请稍后重试")
            return
        
        # 显示警告（如果使用模拟数据）
        if is_mock:
            st.markdown("""
            <div class="warning-box">
                <strong>⚠️ 提示：</strong> 由于云端访问受限或网络问题，当前展示的是演示数据。
                建议本地部署或使用代理服务以获取真实数据。
            </div>
            """, unsafe_allow_html=True)
        
        # 价格统计
        df = pd.DataFrame(products)
        prices = df['price'].tolist()
        
        st.markdown("---")
        st.markdown("## 📊 价格统计")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("商品数量", len(products))
        with col2:
            st.metric("最高价格", f"${max(prices):.2f}")
        with col3:
            st.metric("最低价格", f"${min(prices):.2f}")
        with col4:
            st.metric("平均价格", f"${sum(prices)/len(prices):.2f}")
        
        # 商品展示
        st.markdown("---")
        st.markdown("## 🛍️ 商品列表")
        
        # 使用列布局展示商品
        cols_per_row = 3
        for i in range(0, len(products), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(products):
                    product = products[i + j]
                    with cols[j]:
                        # 显示图片
                        if product['image_url']:
                            try:
                                st.image(product['image_url'], use_container_width=True)
                            except:
                                st.image('https://via.placeholder.com/300x300.png?text=No+Image', use_container_width=True)
                        
                        # 显示标题
                        st.markdown(f"**{product['title'][:50]}...**" if len(product['title']) > 50 else f"**{product['title']}**")
                        
                        # 显示价格
                        st.markdown(f"<span style='color: #e74c3c; font-size: 1.3rem; font-weight: bold;'>${product['price']:.2f}</span>", unsafe_allow_html=True)
                        
                        # 显示链接
                        if product['product_url']:
                            st.markdown(f"[查看详情]({product['product_url']})")
                        
                        st.markdown("---")
        
        # 数据表格
        with st.expander("📋 查看完整数据表"):
            st.dataframe(df[['title', 'price', 'currency']], use_container_width=True)

if __name__ == "__main__":
    main()
