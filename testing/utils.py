"""
Utility function for testing


TODO learn how to import it properly

"""

def print_header(text: str):
    """
    prints header in this formmat:
    ========
    = text =
    ========
    """
    mult = len(text) + 4
    print("=" * mult)
    print(f"= {text} =")
    print("=" * mult)
