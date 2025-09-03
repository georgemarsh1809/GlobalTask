from .terms import (
    PROHIBITED_THEMES_KEYWORDS, 
    AGE_PROHIBITED_THEMES_KEYWORDS,
    RESTRICTED_THEMES_KEYWORDS,
    RESTRICTED_COUNTRY_KEYWORDS
)
from .constants import (
    STATUS_APPROVED,
    STATUS_REJECTED,
    STATUS_REQUIRES_REVIEW
)
from .models import Metadata
from .services import is_child_audience, is_child_placement

def check_filename(filename: str) -> tuple[str, list[str]]:
    text = filename.lower()
    reasons = []

    for word in PROHIBITED_THEMES_KEYWORDS:
        if word in text:
            return STATUS_REJECTED, [f"Prohibited term in filename: {word}"]

    for word in RESTRICTED_THEMES_KEYWORDS:
        if word in text:
            reasons.append(f"Restricted term in filename: {word}")

    for word in RESTRICTED_COUNTRY_KEYWORDS:
        if word in text:
            reasons.append(f"Restricted country name in filename: {word}")

    if reasons:
        return STATUS_REQUIRES_REVIEW, reasons

    return STATUS_APPROVED, []

def check_metadata(meta: Metadata) -> tuple[str, list[str]]:
    reasons = []
    text_fields = [meta.market, meta.placement, meta.audience, meta.category]

    # Flatten into a single lowercase string for scanning
    combined_text = " ".join([t for t in text_fields if t]).lower()

    placement = (meta.placement or "").lower()
    market = (meta.market or "").lower()
    
    # Check for child related audience - if audience is children, 
    #   and if category includes age restricted themes → auto-reject.
    #   else, append a new reason, prompting at least a requires_review status
    if is_child_audience(meta.audience):
        if meta.category and any(
            word in (meta.category or "").lower()
            for word in AGE_PROHIBITED_THEMES_KEYWORDS
        ):
            return STATUS_REJECTED, [f"Child-related audience found: {meta.audience}. Category not allowed."]

        reasons.append(f"Child-related audience found: {meta.audience}")
    
    if is_child_placement(placement):
        if meta.category and any(
            word in (meta.category or "").lower()
            for word in AGE_PROHIBITED_THEMES_KEYWORDS
        ):
            return STATUS_REJECTED, [f"Child-related placement found: {placement}. Category not allowed."]

        reasons.append(f"Child-related placement found: {placement}")

        # Check for prohibited themes in metadata → instantly return a reject
    for word in PROHIBITED_THEMES_KEYWORDS:
        if word in combined_text:
            return STATUS_REJECTED, [f"Prohibited term found in metadata: {word}"]
        
    # Check for age restricted → add reason to reasons array, prompting requires_review response
    for word in AGE_PROHIBITED_THEMES_KEYWORDS:
        if word in combined_text :
            reasons.append(f"Age restricted term found in metadata: {word}")

    # Check for restricted themes → add reason to reasons array, prompting requires_review response
    for word in RESTRICTED_THEMES_KEYWORDS:
        if word in combined_text:
            reasons.append(f"Restricted term found in metadata: {word}")

    # If there is a market (country), check its not in the restricted countries list
    if market:
        for country in RESTRICTED_COUNTRY_KEYWORDS:
            if country in market:
                reasons.append(f"Restricted country found in metadata: {country}")

    if reasons:
        return STATUS_REQUIRES_REVIEW, reasons

    return STATUS_APPROVED, []

