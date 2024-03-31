You will need to run the following commands to pull down ollama models the first time you run this:

```bash
curl http://localhost:11434/api/pull -d '{
  "name": "llama2"
}'

curl http://localhost:11434/api/pull -d '{
  "name": "nomic-embed-text"
}'
```