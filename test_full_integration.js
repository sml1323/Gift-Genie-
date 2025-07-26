#!/usr/bin/env node
/**
 * Full Integration Test - Frontend API client to Backend
 * Test the complete flow using the frontend API client
 */

const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';

// Test request payload (matches frontend format)
const TEST_REQUEST = {
  recipient_age: 28,
  recipient_gender: "여성",
  relationship: "친구",
  budget_min: 50,
  budget_max: 150,
  interests: ["독서", "커피", "여행", "사진"],
  occasion: "생일",
  personal_style: "미니멀리스트",
  restrictions: ["쥬얼리 제외"]
};

async function testFrontendAPIFlow() {
  console.log('🌐 Testing Frontend API Flow');
  console.log('=' + '='.repeat(50));
  
  try {
    // Test 1: Health Check
    console.log('\n🏥 Testing health check...');
    const healthResponse = await axios.get(`${API_BASE_URL}/api/v1/health`);
    console.log(`✅ Health check passed: ${healthResponse.data.status}`);
    
    // Test 2: Main recommendation flow (what frontend will actually call)
    console.log('\n🎁 Testing main recommendation flow...');
    const startTime = Date.now();
    
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/recommendations/naver`,
      TEST_REQUEST,
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 30000 // 30 second timeout
      }
    );
    
    const duration = (Date.now() - startTime) / 1000;
    
    if (response.status === 200) {
      const data = response.data;
      
      console.log(`✅ API call successful (${duration.toFixed(2)}s)`);
      console.log(`   Request ID: ${data.request_id}`);
      console.log(`   Recommendations: ${data.recommendations?.length || 0}`);
      console.log(`   Search Results: ${data.search_results?.length || 0}`);
      console.log(`   Simulation Mode: ${data.simulation_mode}`);
      console.log(`   Total Time: ${data.total_processing_time?.toFixed(2)}s`);
      
      // Validate response structure
      const requiredFields = ['request_id', 'recommendations', 'search_results', 'pipeline_metrics'];
      const missingFields = requiredFields.filter(field => !(field in data));
      
      if (missingFields.length === 0) {
        console.log('✅ Response structure is valid');
      } else {
        console.log(`⚠️  Warning: Missing fields: ${missingFields.join(', ')}`);
      }
      
      // Show sample recommendation
      if (data.recommendations && data.recommendations.length > 0) {
        const rec = data.recommendations[0];
        console.log('\n📋 Sample Recommendation:');
        console.log(`   Title: ${rec.title}`);
        console.log(`   Price: $${rec.estimated_price}`);
        console.log(`   Category: ${rec.category}`);
        console.log(`   Confidence: ${rec.confidence_score?.toFixed(2)}`);
        
        if (rec.purchase_link) {
          console.log(`   Purchase: ${rec.purchase_link.substring(0, 50)}...`);
        }
      }
      
      // Show sample search result
      if (data.search_results && data.search_results.length > 0) {
        const result = data.search_results[0];
        console.log('\n🔍 Sample Search Result:');
        console.log(`   Title: ${result.title}`);
        console.log(`   Domain: ${result.domain}`);
        console.log(`   Price: $${result.price}`);
      }
      
      return true;
    } else {
      console.log(`❌ API call failed with status: ${response.status}`);
      return false;
    }
    
  } catch (error) {
    console.log(`❌ Integration test failed: ${error.message}`);
    
    if (error.response) {
      console.log(`   HTTP Status: ${error.response.status}`);
      console.log(`   Error Data: ${JSON.stringify(error.response.data, null, 2)}`);
    }
    
    return false;
  }
}

async function testFrontendCompatibility() {
  console.log('\n🔗 Testing Frontend Compatibility');
  console.log('=' + '='.repeat(40));
  
  // Test the exact endpoints that frontend API client will use
  const endpoints = [
    '/api/v1/health',
    '/api/v1/recommendations/naver',
    '/api/v1/recommendations/enhanced'
  ];
  
  for (const endpoint of endpoints) {
    try {
      if (endpoint === '/api/v1/health') {
        const response = await axios.get(`${API_BASE_URL}${endpoint}`);
        console.log(`✅ ${endpoint}: ${response.status} OK`);
      } else {
        const response = await axios.post(
          `${API_BASE_URL}${endpoint}`,
          TEST_REQUEST,
          { headers: { 'Content-Type': 'application/json' }, timeout: 10000 }
        );
        console.log(`✅ ${endpoint}: ${response.status} OK (${response.data.recommendations?.length || 0} recs)`);
      }
    } catch (error) {
      console.log(`❌ ${endpoint}: ${error.response?.status || 'ERROR'} - ${error.message}`);
    }
  }
}

async function main() {
  console.log('🚀 Gift Genie Full Integration Test');
  console.log('=' + '='.repeat(60));
  console.log('Testing complete frontend → backend flow\n');
  
  const success1 = await testFrontendAPIFlow();
  await testFrontendCompatibility();
  
  console.log('\n📊 Final Results');
  console.log('=' + '='.repeat(30));
  
  if (success1) {
    console.log('🎉 ✅ Frontend-Backend integration is WORKING!');
    console.log('🌐 Frontend (http://localhost:3000) ↔ Backend (http://localhost:8000)');
    console.log('📱 You can now test the complete user flow in the browser');
  } else {
    console.log('❌ Integration test failed. Please check the errors above.');
  }
}

// Run the test
main().catch(console.error);