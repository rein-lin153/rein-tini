#!/bin/bash
# 音乐系统测试脚本

echo "🎵 音乐系统测试脚本"
echo "===================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试配置
BASE_URL="http://localhost:5000"
ADMIN_TOKEN="${ADMIN_UPLOAD_TOKEN:-changeme123}"

# 测试函数
test_endpoint() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local expected_status=$5
    
    echo -n "测试 $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" -H "Authorization: Bearer $ADMIN_TOKEN" $data "$url")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $http_code)"
        return 0
    else
        echo -e "${RED}✗ 失败${NC} (HTTP $http_code, 期望 $expected_status)"
        echo "响应: $body"
        return 1
    fi
}

# 测试 1: 获取音乐列表
echo "1. 测试获取音乐列表"
test_endpoint "GET /music/list" "GET" "$BASE_URL/music/list" "" "200"
echo ""

# 测试 2: 播放器页面
echo "2. 测试播放器页面"
test_endpoint "GET /music/player" "GET" "$BASE_URL/music/player" "" "200"
echo ""

# 测试 3: 上传页面（需要登录，可能会重定向）
echo "3. 测试上传页面"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/music/admin/upload")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "200" ] || [ "$http_code" = "302" ]; then
    echo -e "${GREEN}✓ 通过${NC} (HTTP $http_code)"
else
    echo -e "${YELLOW}⚠ 警告${NC} (HTTP $http_code, 可能需要登录)"
fi
echo ""

# 测试 4: 获取背景图列表
echo "4. 测试获取背景图列表"
test_endpoint "GET /music/backgrounds" "GET" "$BASE_URL/music/backgrounds" "" "200"
echo ""

# 测试 5: 上传音乐（如果没有测试文件，会失败）
echo "5. 测试上传音乐 API"
if [ -f "test.mp3" ]; then
    test_endpoint "POST /music/upload" "POST" "$BASE_URL/music/upload" "-F file=@test.mp3 -F title=测试歌曲 -F artist=测试艺术家" "200"
else
    echo -e "${YELLOW}⚠ 跳过${NC} (未找到 test.mp3 文件)"
fi
echo ""

# 测试 6: 无效令牌
echo "6. 测试无效令牌"
response=$(curl -s -w "\n%{http_code}" -X POST -H "Authorization: Bearer invalid-token" "$BASE_URL/music/upload")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" = "403" ]; then
    echo -e "${GREEN}✓ 通过${NC} (正确拒绝无效令牌)"
else
    echo -e "${YELLOW}⚠ 警告${NC} (HTTP $http_code, 可能允许了无效令牌)"
fi
echo ""

# 总结
echo "===================="
echo "测试完成！"
echo ""
echo "提示："
echo "- 如果某些测试失败，请检查 Flask 应用是否正在运行"
echo "  运行: flask run"
echo "- 上传测试需要有效的 MP3 文件"
echo "- 某些测试可能需要管理员登录"
echo ""

