def add_email_footer(message):
    footer = """
-------------------------------------------------

Trans Care Agencies Ltd
Clean Cooking Energy  & Engineering Solutions

P.O. Box 396-30100, Eldoret
Eldoret, Kenya

Tel: +254 713 147392
Email: info@transcare.co.ke
Website: www.transcare.co.ke

This is an automated message. Please do not reply directly to this email.

-------------------------------------------------
"""
    return f"{message.strip()}\n\n{footer.strip()}"
