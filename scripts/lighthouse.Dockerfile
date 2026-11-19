# Lighthouse (the engine behind Google PageSpeed Insights) with a headless Chromium, on the project's Node version.
FROM node:26-alpine
RUN apk add --no-cache chromium font-noto font-noto-emoji \
    && npm install -g --no-audit --no-fund lighthouse
ENV CHROME_PATH=/usr/bin/chromium-browser
