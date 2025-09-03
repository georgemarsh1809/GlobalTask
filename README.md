# 🚀 Creative Approval API – Setup Instructions

## Overview

This API validates uploaded creative files (images) against advertising
standards including the Global Outdoor Copy Approval Guidelines and ASA CAP Code
(UK). The service performs automated checks to determine if content should be
approved, rejected, or requires manual review.

You can run it locally or via Docker.

### Validation Logic

The system categorizes content into three outcomes:

-   **APPROVED**: Content meets all guidelines and can be used.
-   **REJECTED**: Content contains prohibited elements and cannot be used.
-   **REQUIRES_REVIEW**: Content contains restricted elements requiring manual
    review.

### Implemented Checks

1. **File Format & Technical Validation**

    - Supports PNG, JPEG, and small GIF files
    - Validates dimensions, file size, and aspect ratios
    - Checks for low contrast or accessibility issues
    - Flags flashing GIFs or high frame rates for review

2. **Content Filtering**

    - Filename and metadata analysis:
        - Prohibited terms detection (tobacco, weapons, explicit content, etc.)
        - Restricted terms detection (crypto, gambling, etc.)
        - Age restricted terms (alcohol, energy drink, etc.)

3. **Context-Aware Validation**
    - Location-based restrictions (e.g., alcohol near schools)
    - Market-specific content restrictions
    - Audience-appropriate content validation

The validation logic interprets prohibited content (directly rejected) versus
restricted content (requires review) based on established advertising
guidelines.

## 🔧 Local Setup

### Prerequisites

-   Python **3.11+**
-   pip or Poetry for dependency management

### Steps

1. Clone the repository:

```bash
git clone https://github.com/georgemarsh1809/GlobalTask.git
cd GlobalTask
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the API locally:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

5. Open the interactive API docs in your browser: 👉 http://localhost:8000/docs

## 🐳 Run with Docker

### Prerequisites

-   Docker installed and running

### Steps

1. Build the image:

```bash
docker build -t creative-approval-api .
```

2. Run the container:

```bash
docker run -p 8000:8000 creative-approval-api
```

3. Open the interactive API docs: 👉 http://localhost:8000/docs

I also included a `docker-compose.yml` file so that during development, hot
reload can be used - when edits are made, the app will restart automatically
when you edit code.

To run in this development mode:

```bash
docker-compose up --build
```

## 🧪 3. Run Tests

The project uses **pytest** with tiny test images generated at runtime.

Locally:

```bash
pytest -v
```

In Docker:

```bash
docker run creative-approval-api pytest -v
```

You can also test the API with an API platform like Postman. This will allow you
to upload real images and a metadata string. \

→ **Note that there is an error handler for forbidden metadata keys. Any
unexpected keys will throw a 422 response.**

## 🔌 API Endpoints

-   `GET /health` → Service status
-   `POST /creative-approval` → Upload a creative for validation
    -   **Input**: multipart form with:
        -   `file`: PNG/JPEG/small GIF
        -   `metadata`: optional JSON string (`market`, `placement`, `audience`,
            `category`)
    -   **Output**: JSON with:
        -   `status`: `"APPROVED"`, `"REJECTED"`, `"REQUIRES_REVIEW"`
        -   `reasons`: list of reasons if status is `"REJECTED"` or
            `"REQUIRES_REVIEW"`
        -   `img_format`, `img_width`, `img_height`, `img_size`

## 🧠 My Approach

1. Built a FastAPI server with two required endpoints.
2. Created a Dockerfile to containerize the service on port 8000.
3. Reviewed policies to determine prohibited vs restricted checks.
4. Create backend services for each check
5. Update FastAPI endpoints to receive file and run services

Considering the 3 possible outcomes, it was important to interpret the
difference between prohibited and restricted creative content from the 2
policies. These forms of content can be directly mapped to an outcome:

-   Prohibited content (not allowed) → REJECTED
-   Restricted content (advice needed) → REQUIRES_REVIEW If the creative content
    contains copy that is determined neither prohibited nor restricted, the
    creative is suitable for approval. \

Considering that the scope of this project requires only 2/3 checks, it’s
important that the checks cover as many rules/heuristics from BOTH policies as
appropriately possible.

The scope of the project doesn't require heavy ML services, so it’s not
appropriate to analyse the exact content of the ads (such as text). This limits
the scope to other properties of the files, such as filenames, metadata, image
properties (format, size, aspect ratio, contrast etc.), and also simple
heuristics;

-   For example, a very low contrast may mean the text is not suitable, or large
    aspect ratios meaning its not appropriate for outdoor use.

### High-Level Outcome Mapping:

Prohibited → REJECTED

Restricted → REQUIRES_REVIEW

Otherwise → APPROVED

By splitting the checks into direct mappings to rejected/required review
outcomes, this allows for faster interpretation of the policies - instead of
reading every line, the focus can be on highlighting the rules in each document
that fall under either prohibited or restricted content.

### Implemented Checks + Policy References

1. **File Format / Size / Dimensions / Aspect Ratio / Contrast / File
   Complexity**

-   Reject unsupported formats (non-JPEG/PNG/GIF), as defined in brief.
-   Low contrast or tiny dimensions → REQUIRES_REVIEW.
    -   Justified by:
        -   Global Guidelines (require ads not to disorient or confuse the
            public, and to meet accessibility expectations).
        -   CAP Code Section 4.7 (visual effects harmful to certain groups).
        -   CAP Code Section 1.3 (responsibility to consumers, including clear,
            readable messaging).
-   Flashing GIFs or very high frame rates → flag for review.
    -   Justified by:
        -   Global Outdoor Copy Approval Guidelines → explicitly bans fast
            flashing/disorientating visuals.
        -   ASA CAP Code → bans harmful visual effects (Section 4.7).

2. **Prohibited & Restricted Keyword Filtering of Filenames and Metadata**

-   Filter against prohibited terms (tobacco, casino, porn, weapon, etc.) and
    restricted terms (crypto, gambling, alcohol, etc.).

    -   Global Guidelines define prohibited/restricted categories.
    -   ASA CAP Code defines specific prohibited/restricted themes:
        -   **Tobacco** (Section 21) - full restriction (**auto-reject**).
        -   **Alcohol** (Section 18) - restrictions on portrayal and placement.
            **If audience is under 18, then creative rejected** (18.14).
        -   **Medicines, health, beauty** (Section 12) - restricts
            health/medical claims, **requires review and substantiation**
            (12.1).
        -   **Electronic cigarettes** (Section 22) - **If audience is under 18,
            then creative rejected** (22.11)
        -   **Environmental claims** (Section 11) - requires review and
            substantiation (11.3).
        -   **Weight control / slimming** (Section 13) → avoids exploitative or
            misleading slimming claims, requires review and substantiation. If
            audience is under 18, then creative prohibited (13.3)
        -   **Gambling** (Section 16) → restricted category. **If audience is
            under 18, then creative prohibited** (16.3.13).
        -   **Food, supplements & nutrition** (Section 15) → Restrictions on ads
            related to HFSS food (high fat, sugar, salt) issues, ** requires
            review and substantiation** (15.1).

    These themes were parsed to ChatGPT to create a list of terms that are
    stored in an array in terms.py, which filenames and metadata are checked
    against.

3. **Metadata-based checks** (if parsed)

-   e.g.
    -   If `placement=school` and creative mentions age restricted themes
        (alcohol/gambling) → REJECT.
    -   If market is in banned countries list → REQUIRES_REVIEW.
-   Meta-data properties include:
    -   Placement
    -   Audience
    -   Market (country)
    -   Category (any themes listed in the policy interpretations (e.g. alcohol,
        tobacco, crypto)

### 🤖 Use of GenAI:

I used ChatGPT Plus to speed up some aspects of the project workflow, including;

-   General debugging/syntax validation
-   Key info extraction from ASA CAP Code due to large file size. Relevant
    rules, restrictions and prohibitions were reviewed and linked to rule
    section numbers by me for full understanding - the sections can be seen
    below.
-   Generation of restricted and prohibited terms lists (terms.py)
-   Scaffolding of Pytest suite

### 🎨 Design Decisions & Trade-Offs

-   **No OCR / Content Parsing**: The brief did not require heavy ML or text
    recognition, so copy inside images is not analysed. Checks are limited to
    filenames, metadata, and file properties.

-   **Keyword Lists Only**: Restricted/prohibited content detection uses curated
    keyword lists rather than NLP or AI classification. This is deterministic,
    fast, and transparent.

-   **Lightweight Image Checks**: Contrast, aspect ratio, and GIF complexity are
    measured with simple heuristics (e.g., standard deviation of brightness,
    frame count, FPS) instead of advanced computer vision.

-   **Single Container**: The API runs as one service (FastAPI + Uvicorn). No
    database or external storage is included, since persistence was not
    necessary inside scope.

### ➡️ Future Prospects: What I Would Do Next

-   **Add OCR For Copy Checks**: Utilise OpenAI OCR capabilities to scan text
    inside creatives for prohibited/restricted terms/images. This would align
    the system more closely with real-world advertising review.

-   **Database Integration**: Store submission logs, decisions, and rejected
    creatives in a database (e.g., Postgres) for auditability.

-   **Admin Dashboard**: Build a lightweight front-end for reviewers to see
    flagged creatives and override automated decisions.

-   **Policy Expansion**: Add checks for accessibility (e.g. WCAG contrast
    thresholds), localisation (cultural sensitivity per market), and more
    advanced legibility heuristics.

-   **Test With Real Creatives**: Add a richer test suite with real-world sample
    ads across both compliant and non-compliant cases.
