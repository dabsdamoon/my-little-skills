---
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---
Our OpenAI support bot got expensive. Every request sends the same ~6K-token block of instructions and product docs, then the customer's question, but the usage logs show `cached_tokens` is 0 on almost every call. The request is built like this:

```python
instructions = f"Current time: {datetime.now().isoformat()}\nCustomer: {customer.name}\n\n{SUPPORT_RULES}\n\n{PRODUCT_DOCS}"
response = client.responses.create(model=MODEL, instructions=instructions, input=question)
```

Why isn't caching kicking in, and how should I restructure this so we stop paying full price for the same tokens every time?
