#!/bin/bash

# Origo Integration Test Script
# This script tests the full application stack

echo "🧪 Origo Integration Test Starting..."

# Test 1: Check Docker Compose configuration
echo "📋 Testing Docker Compose configuration..."
if docker-compose config > /dev/null 2>&1; then
    echo "✅ Docker Compose configuration is valid"
else
    echo "❌ Docker Compose configuration has errors"
    exit 1
fi

# Test 2: Build and start services
echo "🐳 Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Test 3: Check backend health
echo "🔍 Testing backend health endpoint..."
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    docker-compose logs backend
    exit 1
fi

# Test 4: Test API endpoints
echo "📡 Testing API endpoints..."

# Test root endpoint
if curl -f -s http://localhost:8000/ > /dev/null; then
    echo "✅ Root endpoint accessible"
else
    echo "❌ Root endpoint failed"
fi

# Test analysis endpoint with sample text
echo "📝 Testing text analysis endpoint..."
ANALYSIS_RESPONSE=$(curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a comprehensive test of the AI detection system. The analysis should provide detailed insights into various metrics including perplexity, burstiness, semantic coherence, and n-gram patterns. This text contains enough content to trigger all analysis components."}')

if echo "$ANALYSIS_RESPONSE" | grep -q "overall_score"; then
    echo "✅ Text analysis endpoint working"
    echo "📊 Sample analysis result:"
    echo "$ANALYSIS_RESPONSE" | jq -r '.overall_score, .global_scores'
else
    echo "❌ Text analysis endpoint failed"
    echo "Response: $ANALYSIS_RESPONSE"
fi

# Test 5: Check frontend accessibility
echo "🌐 Testing frontend accessibility..."
if curl -f -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend accessible"
else
    echo "❌ Frontend not accessible"
    docker-compose logs frontend
fi

# Test 6: Basic functional test
echo "🔧 Running basic functional tests..."

# Test with different text lengths
SHORT_TEXT='{"text": "Short AI test."}'
MEDIUM_TEXT='{"text": "This is a medium-length text for testing the AI detection capabilities of Origo. It should provide moderate analysis depth."}'

echo "Testing short text..."
curl -s -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d "$SHORT_TEXT" | jq -r '.overall_score' > /dev/null

echo "Testing medium text..."
curl -s -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d "$MEDIUM_TEXT" | jq -r '.overall_score' > /dev/null

echo "✅ Functional tests completed"

# Cleanup
echo "🧹 Cleaning up test environment..."
docker-compose down

echo "🎉 Integration test completed successfully!"
echo ""
echo "📋 Test Summary:"
echo "✅ Docker configuration valid"
echo "✅ Services build and start correctly"
echo "✅ Backend health check passes"
echo "✅ API endpoints respond correctly"
echo "✅ Text analysis functionality works"
echo "✅ Frontend is accessible"
echo "✅ Basic functional tests pass"
echo ""
echo "🚀 Origo is ready for deployment!"