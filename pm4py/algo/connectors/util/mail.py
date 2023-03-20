from typing import Optional


def connect(email_user: Optional[str], mailbox_id: int):
    """
    Returns a mailbox object from the local Outlook instance.

    Parameters
    -------------
    email_user
        E-mail address to use
    mailbox_id
        ID of the mailbox to use:
        * 5 = outbox
        * 6 = inbox
        * 9 = calendar

    Returns
    -------------
    mailbox_obj
        Mailbox object
    """
    import win32com.client

    outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
    mailbox_id = int(mailbox_id)

    if email_user is not None:
        recipient = outlook.CreateRecipient(email_user)
        recipient.Resolve()
        return outlook.GetSharedDefaultFolder(recipient, mailbox_id)

    return outlook.GetDefaultFolder(mailbox_id)
