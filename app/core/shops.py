"""Gli shop di cui mostriamo i prezzi (eBay e Amazon esclusi: prezzi poco affidabili)."""

from dataclasses import dataclass
from urllib.parse import quote_plus


@dataclass(frozen=True)
class Shop:
    column: str
    label: str
    currency: str
    search_url: str  # {q} viene sostituito dal nome della carta

    def link(self, card_name: str) -> str:
        return self.search_url.format(q=quote_plus(card_name))

    def fmt(self, price: float | None) -> str:
        return "-" if price is None else f"{self.currency} {price:,.2f}"


SHOPS = [
    Shop(
        "price_cardmarket", "Cardmarket", "€",
        "https://www.cardmarket.com/en/YuGiOh/Products/Search?searchString={q}",
    ),
    Shop(
        "price_tcgplayer", "TCGplayer", "$",
        "https://www.tcgplayer.com/search/yugioh/product?q={q}",
    ),
    Shop(
        "price_coolstuffinc", "CoolStuffInc", "$",
        "https://www.coolstuffinc.com/main_search.php?pa=searchOnName&page=1&resultsPerPage=25&q={q}",
    ),
]

BY_LABEL = {s.label: s for s in SHOPS}
