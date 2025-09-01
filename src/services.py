import PIL
from .terms import PROHIBITED_THEMES_KEYWORDS, AGE_PROHIBITED_THEMES_KEYWORDS, RESTRICTED_COUNTRY_KEYWORDS, RESTRICTED_THEMES_KEYWORDS


# 1. File Props
# check format
def check_format(file):
    pass

# check size (mb)
def check_size(file):
    pass

# check dimensions/resolution
def check_resolution(file):
    pass

# check aspect ratio
def check_aspect_ratio(file):
    pass

# check contrast
def check_contrast(file):
    pass

# check file complexity
def check_complexity(file):
    pass


# 2. Keyword Matches
# check against PROHIBITED_THEMES_KEYWORDS
# respond with REJECTION or None

# check against RESTRICTED_COUNTRY_KEYWORDS
# respond with REQUIRES_REVIEW or None

# check against RESTRICTED_THEMES_KEYWORDS
# respond with REQUIRES_REVIEW or None


# 3. Meta-data based checks (if parsed)
# check against AGE_PROHIBITED_THEMES_KEYWORDS  
# respond with REJECTION or None
