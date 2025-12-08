# Legal Compliance

This document outlines how this project complies with web scraping best practices and respects the robots.txt directives of the websites it interacts with.

## Robots.txt Compliance

### Shopee Philippines (shopee.ph)

We respect Shopee's robots.txt directives:

| Directive                         | Our Compliance                                                         |
| --------------------------------- | ---------------------------------------------------------------------- |
| `Crawl-delay: 1`                  | ✅ We use a **5-second delay** between requests (5x more conservative) |
| `Disallow: /cart/`                | ✅ We do not access cart pages                                         |
| `Disallow: /checkout/`            | ✅ We do not access checkout pages                                     |
| `Disallow: /user/`                | ✅ We do not access user pages                                         |
| `Disallow: /search*searchPrefill` | ✅ We do not use searchPrefill parameter                               |
| `Disallow: /search?shop=`         | ✅ We do not search within specific shops                              |
| `Disallow: /shop/*/search`        | ✅ We do not use shop-specific search                                  |

**Allowed endpoints we use:**

- `/search?keyword={query}&page={n}` - General product search (NOT disallowed)

### Lazada Philippines (lazada.com.ph)

We respect Lazada's robots.txt directives:

| Directive                                   | Our Compliance                         |
| ------------------------------------------- | -------------------------------------- |
| `Disallow: /wow/gcp/ph/member/login-signup` | ✅ We do not access login/signup pages |
| `Disallow: /undefined/`                     | ✅ We do not access undefined routes   |

**Allowed endpoints we use:**

- `/catalog/?q={query}&page={n}` - Product catalog search (NOT disallowed)

## Rate Limiting

To minimize server impact, we implement conservative rate limiting:

| Measure                    | Implementation                                       |
| -------------------------- | ---------------------------------------------------- |
| Request Delay              | 5 seconds between page requests (with random jitter) |
| Scheduling                 | Scraping runs once daily at 6:00 AM UTC              |
| Pagination Limit           | Configurable max pages per search (default: 5)       |
| No User-Triggered Scraping | Frontend search only queries local database          |

## Data Usage

- **Purpose**: Price tracking and comparison for personal/educational use
- **Storage**: Only publicly available product information (title, price, images)
- **No PII**: We do not collect or store any personal user information
- **No Authentication Bypass**: We do not access any authenticated/protected content

## Best Practices Followed

1. **Respectful Crawling**: Delays exceed robots.txt requirements
2. **Honest User-Agent**: We identify ourselves appropriately
3. **Minimal Footprint**: Only scrape necessary public data
4. **Scheduled Operations**: No real-time scraping triggered by users
5. **Error Handling**: Graceful backoff on errors, no aggressive retries

## Disclaimer

This project is for educational and personal use. Users are responsible for ensuring their use of this software complies with applicable laws and the terms of service of the websites being accessed.

If you are a representative of Shopee or Lazada and have concerns about this project, please open an issue and we will address it promptly.

---

_Last updated: December 2024_
