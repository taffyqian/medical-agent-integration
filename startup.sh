#!/bin/bash
# Azure App Service (Linux) 启动脚本
# 用途：启动 Streamlit，绑定到 Azure 注入的端口

# 默认端口 8000（Azure 会通过 WEBSITES_PORT 或 PORT 注入实际端口）
PORT_TO_USE="${PORT:-${WEBSITES_PORT:-8000}}"

echo "Starting Streamlit on port $PORT_TO_USE"

python -m streamlit run app.py \
    --server.port "$PORT_TO_USE" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false