FROM nginx

COPY dist/  /usr/share/nginx/html/

COPY nginx/default.conf /etc/nginx/templates/default.conf.template

# 复制入口脚本
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# 赋予执行权限
RUN chmod +x /usr/local/bin/entrypoint.sh

# 设置入口点
ENTRYPOINT ["entrypoint.sh"]

# 启动方式

# docker run --name [contain_name] -e API_PROXY_URL=[api_url] -p [port]:80 [image_name]

