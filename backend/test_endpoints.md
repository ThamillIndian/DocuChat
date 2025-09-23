# Endpoint Testing Guide

## Base URL: `http://localhost:8000`

## 1. Health Check
**Endpoint:** `GET /healthz`

**Request:**
```bash
curl -X GET "http://localhost:8000/healthz"
```

**Expected Response:**
```json
{
  "ok": true
}
```

---

## 2. Create New Session
**Endpoint:** `POST /session/new`

**Request:**
```bash
curl -X POST "http://localhost:8000/session/new"
```

**Expected Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Save the session_id for subsequent requests!**

---

## 3. Upload Files to Session
**Endpoint:** `POST /session/{session_id}/upload`

**Request (with text file):**
```bash
curl -X POST "http://localhost:8000/session/YOUR_SESSION_ID/upload" \
  -F "files=@sample.txt"
```

**Create test files first:**
```bash
# Create sample.txt
echo "This is a sample document about artificial intelligence. AI has revolutionized many industries including healthcare, finance, and transportation. Machine learning algorithms can now process vast amounts of data to make predictions and decisions." > sample.txt

# Create sample.mp3 (dummy audio file)
echo "This is a dummy audio file for testing ASR functionality." > sample.mp3
```

**Request (multiple files):**
```bash
curl -X POST "http://localhost:8000/session/YOUR_SESSION_ID/upload" \
  -F "files=@sample.txt" \
  -F "files=@sample.mp3"
```

**Expected Response:**
```json
{
  "added": [
    {
      "source_id": "123e4567-e89b-12d3-a456-426614174000",
      "filename": "sample.txt",
      "len": 180
    },
    {
      "source_id": "987fcdeb-51a2-43d1-b789-123456789abc",
      "filename": "sample.mp3", 
      "len": 65
    }
  ],
  "total_chunks": 2
}
```

---

## 4. Chat with Streaming Response
**Endpoint:** `POST /chat/stream`

**Request:**
```bash
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "session_id": "YOUR_SESSION_ID",
    "message": "What is artificial intelligence?",
    "k": 5,
    "max_ctx": 4000
  }'
```

**Expected Response (Server-Sent Events):**
```
event:meta
data:[{"source_id": "123e4567-e89b-12d3-a456-426614174000", "span": {"chunk": 0}}]

data:[LLM 

data:ANSWER] 

data:This 

data:is 

data:a 

data:sample 

data:document 

data:about 

data:artificial 

data:intelligence. 

data:AI 

data:has 

data:revolutionized 

data:many 

data:industries 

data:including 

data:healthcare, 

data:finance, 

data:and 

data:transportation. 

data:Machine 

data:learning 

data:algorithms 

data:can 

data:now 

data:process 

data:vast 

data:amounts 

data:of 

data:data 

data:to 

data:make 

data:predictions 

data:and 

data:decisions. 

event:done
data:ok
```

---

## 5. Generate Summary
**Endpoint:** `POST /summarize`

**Request:**
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID",
    "mode": "executive"
  }'
```

**Expected Response:**
```json
{
  "summary": "[LLM ANSWER] Summarize the following documents into a concise executive brief with bullet action items.\n\n[123e4567-e89b-12d3-a456-426614174000] This is a sample document about artificial intelligence. AI has revolutionized many industries including healthcare, finance, and transportation. Machine learning algorithms can now process vast amounts of data to make predictions and decisions.\n\n[987fcdeb-51a2-43d1-b789-123456789abc] This is a dummy audio file for testing ASR functionality.",
  "sources": [
    "123e4567-e89b-12d3-a456-426614174000",
    "987fcdeb-51a2-43d1-b789-123456789abc"
  ]
}
```

---

## 6. Delete Session
**Endpoint:** `DELETE /session/{session_id}`

**Request:**
```bash
curl -X DELETE "http://localhost:8000/session/YOUR_SESSION_ID"
```

**Expected Response:**
```json
{
  "ok": true
}
```

---

## Complete Test Script

Create a file called `test_all_endpoints.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "1. Testing Health Check..."
curl -X GET "$BASE_URL/healthz"
echo -e "\n"

echo "2. Creating new session..."
SESSION_RESPONSE=$(curl -s -X POST "$BASE_URL/session/new")
SESSION_ID=$(echo $SESSION_RESPONSE | jq -r '.session_id')
echo "Session ID: $SESSION_ID"
echo -e "\n"

echo "3. Creating test files..."
echo "This is a sample document about artificial intelligence. AI has revolutionized many industries including healthcare, finance, and transportation. Machine learning algorithms can now process vast amounts of data to make predictions and decisions." > sample.txt
echo "This is a dummy audio file for testing ASR functionality." > sample.mp3
echo -e "\n"

echo "4. Uploading files..."
curl -X POST "$BASE_URL/session/$SESSION_ID/upload" \
  -F "files=@sample.txt" \
  -F "files=@sample.mp3"
echo -e "\n"

echo "5. Testing chat stream..."
curl -X POST "$BASE_URL/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d "{\"session_id\": \"$SESSION_ID\", \"message\": \"What is artificial intelligence?\"}"
echo -e "\n"

echo "6. Testing summarize..."
curl -X POST "$BASE_URL/summarize" \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\", \"mode\": \"executive\"}"
echo -e "\n"

echo "7. Cleaning up..."
rm sample.txt sample.mp3
curl -X DELETE "$BASE_URL/session/$SESSION_ID"
echo -e "\n"

echo "All tests completed!"
```

## Error Cases to Test

### 1. Invalid Session ID
```bash
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "invalid-id", "message": "test"}'
```
**Expected:** `404 Not Found`

### 2. Upload Without Files
```bash
curl -X POST "http://localhost:8000/session/YOUR_SESSION_ID/upload"
```
**Expected:** `400 Bad Request`

### 3. Chat Without Uploading Files
```bash
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID", "message": "test"}'
```
**Expected:** `400 Bad Request - "no indexed content; upload first"`

### 4. File Too Large
```bash
# Create a large file (>100MB)
dd if=/dev/zero of=large_file.txt bs=1M count=101
curl -X POST "http://localhost:8000/session/YOUR_SESSION_ID/upload" \
  -F "files=@large_file.txt"
```
**Expected:** `400 Bad Request - "payload too large"`
