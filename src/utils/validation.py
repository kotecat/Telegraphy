from src.models import Account, Page


def is_can_edit(account: Account, page: Page) -> bool:
    return bool(
        (account is not None) and 
        (page is not None) and
        (account.id == page.account_id or account.is_admin)
    )
