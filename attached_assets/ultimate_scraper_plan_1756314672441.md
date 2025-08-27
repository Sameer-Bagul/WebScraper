# Ultimate Web Scraper: Features, Tech Stack & Libraries

## 1. Project Overview

This project has two main purposes:

1. **Job Scraping:** Extract job listings and details based on user-provided domains or keywords (e.g., "Python developer jobs in Berlin").
2. **Lead Scraping for Freelancing:** Find and extract business leads (emails, contact info, company details) to support freelancing outreach and client acquisition.

A **general-purpose web scraper** capable of extracting structured data (emails, URLs, text, metadata) from any website using domain-specific adapters. Built with **FastAPI**, **MongoDB** for storage, **React (Vite)** for UI, and best-in-class scraping libraries for reliability and scalability.

---

## 2. Core Features
---

## 2.6 Purpose-Specific Enhancements

### Job Scraping

* Support for popular job boards (Indeed, LinkedIn, Glassdoor) with prebuilt adapters.
* Keyword and location filters for relevant job results.
* Extract structured job fields: title, company, location, salary, description, apply link.
* Detect and avoid duplicate job postings.
* Schedule recurring job searches for fresh listings.

### Lead Scraping for Freelancing

* Integrate business directories (Yellow Pages, Yelp, Crunchbase) as sources.
* Extract company name, website, email, phone, social links, and business category.
* Enrich leads by crawling company websites for contact info and social profiles.
* Score leads based on relevance (tech stack, location, company size).
* Export leads to CRM tools or Google Sheets for outreach.

### General Enhancements

* Scraping template library for common use cases (jobs, leads, products).
* Simple UI wizard for users to select scraping goal and configure options.
* Anti-bot measures (rotating proxies, captchas) for high-volume scraping.
* Save and reuse search/scraping configurations.
* Analytics to track job/lead acquisition over time.

### 2.1 Scraping Engine

* **Job Scraping:** Search and extract job listings from job boards, company sites, and aggregators using user domain/keyword input.
* **Lead Scraping:** Discover and extract business leads (emails, contact info, company details) for freelancing outreach.
* **DuckDuckGo Search**: Use DuckDuckGo to discover URLs for scraping (web, images, news).
* **Static Scraping**: Fast HTML fetching using Requests + lxml for speed.
* **Dynamic Scraping**: Playwright for JavaScript-heavy websites.
* **Domain Adapters**: JSON-based pluggable selectors for any site.
* **Contact Extraction**: Emails, phones, names, and bios via regex + spaCy NER.
* **Follow Links**: Crawl listing + detail pages automatically.
* **Proxy & User-Agent Rotation**: Avoid blocking with random headers/proxies.
* **Rate Limiting & Retry**: Tenacity for retry logic, ratelimit for throttling.
* **Incremental Scraping**: Skip unchanged pages based on timestamps.

---

### 2.2 Data Handling & Storage

* **Database**: MongoDB for raw HTML, structured data, job metadata.
* **Schema Validation**: Pydantic models for data consistency.
* **Query APIs**: Filter results by domain, timestamp, or field values.

---

### 2.3 Backend API (FastAPI)

* **POST /search**: Search DuckDuckGo for URLs to scrape.
* **POST /scrape**: Start scraping with URLs + adapter.
* **GET /status/{task\_id}**: Fetch job status.
* **GET /results/{task\_id}**: Download results (JSON/CSV).
* **GET /adapters**: List available adapters.
* **POST /adapters**: Add new domain adapters.

---

### 2.4 Frontend (React + Vite + Tailwind)

* **Dashboard**: Monitor job status and statistics.
* **Job Form**: URLs, adapter selection, options (proxies, rate limit).
* **Progress Bar**: Real-time updates via WebSocket/REST polling.
* **Data Table**: Searchable, sortable scraped data.
* **Export Options**: CSV, JSON download.
* **Adapter Manager**: UI to create/edit JSON adapters.

---

### 2.5 Advanced Features

* **Scheduling**: CRON-style job automation.
* **Notifications**: Email/Telegram alerts.
* **Authentication & API Keys**: Secure private access.
* **Analytics Dashboard**: Charts for scrape frequency, errors, runtime metrics.

---

## 3. Libraries & Tools

### 3.1 Scraping Libraries

| Purpose             | Library           | Reason                                        |
| ------------------- | ----------------- | --------------------------------------------- |
| Static Scraping     | Requests + lxml   | Fast, reliable HTML fetching & parsing        |
| Dynamic Scraping    | Playwright        | Best modern headless browser automation       |
| Parsing & Selectors | lxml / Parsel     | Speed + clean CSS/XPath selector support      |
| Contact Extraction  | Regex + spaCy     | Emails, phones, names with NLP-based fallback |
| Retry Logic         | Tenacity          | Robust retry with backoff                     |
| Rate Limiting       | ratelimit         | Avoids site blocking with throttling          |
| DuckDuckGo Search   | duckduckgo-search | Clean API for web, images, news search        |

---

### 3.2 Backend

* **Framework**: FastAPI
* **Task Queue**: Celery + Redis for async jobs
* **Database**: MongoDB (PyMongo / Motor)
* **Validation**: Pydantic

### 3.3 Frontend

* **Framework**: React + Vite
* **UI Library**: Tailwind CSS + ShadCN UI
* **State Management**: Zustand / Redux
* **Data Fetching**: Axios / React Query

### 3.4 Infrastructure

* **Containers**: Docker + Docker Compose
* **Deployment**: AWS / GCP / Render / DigitalOcean
* **Monitoring**: Prometheus + Grafana, Sentry for errors

---

## 4. Workflow

1. User submits search query (DuckDuckGo) or URLs + adapter via React UI.
2. Backend performs DuckDuckGo search (if query provided) and returns URLs.
3. User selects URLs to scrape, submits with adapter.
4. Backend creates Celery job → Scraping starts asynchronously.
5. Static → Dynamic fallback scraping for websites.
6. Data stored in MongoDB with metadata & job status.
7. UI polls API for job status, shows real-time updates.
8. Results downloadable in CSV/JSON.

---

## 5. Roadmap

### Phase 1 (MVP)

* Static scraping, MongoDB integration
* FastAPI API, React + Vite basic UI

### Phase 2

* Playwright dynamic scraping
* Proxy rotation, retry & rate limiting
* Celery-based async jobs, adapter manager UI

### Phase 3

* Scheduling, notifications, authentication
* Analytics dashboard, cloud deployment, monitoring

---

This updated plan removes Google Maps lead generation and focuses entirely on **web scraping** with robust features and scalability.
