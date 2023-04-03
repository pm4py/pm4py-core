'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''

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
    import pythoncom
    pythoncom.CoInitialize()

    import win32com.client

    outlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
    mailbox_id = int(mailbox_id)

    if email_user is not None:
        recipient = outlook.CreateRecipient(email_user)
        recipient.Resolve()
        return outlook.GetSharedDefaultFolder(recipient, mailbox_id)

    return outlook.GetDefaultFolder(mailbox_id)
