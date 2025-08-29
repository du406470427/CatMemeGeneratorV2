# API密钥配置说明

## 环境变量设置

为了保护API密钥安全，本项目使用环境变量来管理敏感信息。请按照以下步骤配置：

### 1. 创建.env文件

在项目根目录创建`.env`文件（如果不存在），并添加以下内容：

```env
# Pexels API密钥
PEXELS_API_KEY=your_pexels_api_key_here

# SiliconFlow API密钥
SILICONFLOW_API_KEY=your_siliconflow_api_key_here

# Google API密钥
GOOGLE_API_KEY=your_google_api_key_here
```

### 2. 获取API密钥

- **Pexels API**: 访问 [https://www.pexels.com/api/](https://www.pexels.com/api/) 注册并获取API密钥
- **SiliconFlow API**: 访问 [https://siliconflow.cn/](https://siliconflow.cn/) 注册并获取API密钥
- **Google API**: 访问 [https://console.developers.google.com/](https://console.developers.google.com/) 创建项目并获取API密钥

### 3. 安全注意事项

- ⚠️ **重要**: `.env`文件已被添加到`.gitignore`中，不会被提交到Git仓库
- 🔒 **不要**将真实的API密钥直接写入配置文件
- 🔒 **不要**将`.env`文件提交到版本控制系统
- 🔒 定期更换API密钥以确保安全

### 4. 使用方法

项目会自动从环境变量中读取API密钥。配置文件中的`${PEXELS_API_KEY}`等占位符会被实际的环境变量值替换。

### 5. 故障排除

如果遇到API密钥相关错误：
1. 确认`.env`文件存在且位于项目根目录
2. 确认API密钥格式正确，没有多余的空格或引号
3. 确认API密钥有效且未过期
4. 重启应用程序以重新加载环境变量