# Tavily Credit Optimization Guide

## Current Configuration (Testing Mode)

### ✅ Optimized for 1 Credit Per Search

```python
response = self.tavily.search(
    query=query,
    topic="news",
    search_depth="basic",      # ⭐ CRITICAL: 1 credit (vs 2+ for "advanced")
    include_images=True,       # No extra cost
    max_results=1              # Testing: 1 result (Production: 10)
)
```

## Credit Breakdown

| Configuration | Credits | Notes |
|--------------|---------|-------|
| `search_depth="basic"` | **1** | ✅ Use this for testing |
| `search_depth="advanced"` | **2+** | ❌ Avoid unless necessary |
| `include_images=True` | **0** | ✅ Free! |
| `max_results=1-10` | **0** | ✅ No extra cost for more results |

## Why You Were Charged 4 Credits

Possible reasons:
1. **Default was "advanced"**: Without explicit `search_depth="basic"`, Tavily defaults to advanced (2 credits)
2. **Multiple calls**: If the code ran twice or had a loop
3. **Auto-upgrade**: Some queries auto-upgrade to advanced depth

## Monthly Budget Planning

**Free Tier**: 1,000 credits/month

### Testing Mode (Current)
- **1 credit per test run**
- Can test **1,000 times/month**

### Production Mode (10 news articles)
- **1 credit per hourly job** (with `search_depth="basic"`)
- **12 jobs per day** (every 2 hours)
- **~360 credits/month**
- **✅ Well within free tier!**

## Switching to Production

When ready to deploy, change this line in `main.py`:

```python
# Change from:
news_list = nf.get_top_news(query="breaking news today", page_size=1)

# To:
news_list = nf.get_top_news(query="breaking news today", page_size=10)
```

Still only **1 credit per call** because `search_depth="basic"` is set!

## Credit Monitoring

Check your usage at: https://app.tavily.com/usage

## Summary

✅ **Current setup**: 1 credit per test  
✅ **Production estimate**: ~360 credits/month  
✅ **Free tier limit**: 1,000 credits/month  
✅ **Headroom**: 640 credits for extra testing/debugging
