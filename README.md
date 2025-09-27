# ThreadPilot (MVP)

本地 FastAPI 服务 + 数据分析端点 + 离线授权占位 + 扩展端口（plugins/config/workflows）。

## 启动（PowerShell）
```powershell
Set-Location D:\ThreadPilot
.\.venv\Scripts\Activate
uvicorn app.main:app --reload
**作用**：项目说明与快速启动提示。

---

# Step 2 自测（请执行并回帖输出）

在同一窗口执行：
```powershell
uvicorn app.main:app --reload
python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" "pydantic-settings" "SQLAlchemy" alembic "passlib[bcrypt]" "python-jose[cryptography]" "python-multipart" stripe pandas numpy openpyxl matplotlib
python -c "import fastapi,uvicorn,pydantic_settings,sqlalchemy,alembic,passlib,jose,multipart,stripe,pandas,numpy,openpyxl,matplotlib; print('OK')"
@'
# ThreadPilot (MVP)

本地 FastAPI 服务 + 数据分析端点 + 离线授权占位 + 扩展端口（plugins/config/workflows）。

## 启动（PowerShell）
```powershell
Set-Location D:\ThreadPilot
.\.venv\Scripts\Activate
uvicorn app.main:app --reload
**解释**：覆盖写入一份简洁的 README，避免前面被截断的内容。

### 3.4 启动服务（开发模式）
```powershell
uvicorn app.main:app --reload
python - << 'PY'
import base64, json, time
license_dict = {
    "exp": int(time.time()) + 365*24*3600,  # 一年后过期
    "plan": "pro",
    "features": ["ai","plugins"],
    "sig": "demo"  # 正式版会用私钥签名，这里只是占位
}
blob = base64.b64encode(json.dumps(license_dict,separators=(',',':')).encode()).decode()
print(blob)
PY
python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" "pydantic-settings" "SQLAlchemy" alembic "passlib[bcrypt]" "python-jose[cryptography]" "python-multipart" stripe pandas numpy openpyxl matplotlib
python -c "import fastapi,uvicorn,pydantic_settings,sqlalchemy,alembic,passlib,jose,multipart,stripe,pandas,numpy,openpyxl,matplotlib; print('OK')"
@'
# ThreadPilot (MVP)

本地 FastAPI 服务 + 数据分析端点 + 离线授权占位 + 扩展端口（plugins/config/workflows）。

## 启动（PowerShell）
Set-Location D:\ThreadPilot
.\.venv\Scripts\Activate
uvicorn app.main:app --reload

打开： http://127.0.0.1:8000/docs
- 健康检查：GET /api/health
- CSV 概览：POST /api/analytics/csv-summary（上传 CSV）
- 激活码写入：POST /api/license/activate（填入 base64 激活码，下次启动生效）
