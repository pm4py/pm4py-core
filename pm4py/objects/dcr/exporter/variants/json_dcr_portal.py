


# {
#    "DCRModel": [
#       {
#          "id": 1002811,
#          "title": "Import App test",
#          "description": "DCR Process",
#          "type": "DCRModel",
#          "roles": [
#             {
#                "title": "Employee",
#                "description": "employee description XXX",
#                "specification": "Employee speficiation XXX"
#             },
#             {
#                "title": "Finance",
#                "description": "finance"
#             },
#             {
#                "title": "Lederen"
#             },
#             {
#                "title": "Manager",
#                "description": "manager ",
#                "specification": "Manager speciication"
#             }
#          ],
#          "events": [
#             {
#                "id": "Case",
#                "label": "When an employee fill out an expense report the mo",
#                "description": "<p>desc W<\/p>\n<p>\"quote in string\"<\/p>\n<p>text<\/p>",
#                "purpose": "Purpose W",
#                "guide": "<p>guide W<\/p>",
#                "type": "subprocess"
#             },
#             {
#                "id": "FilloutExpenseReport",
#                "label": "Fill out an expense report",
#                "roles": "Employee",
#                "datatype": "int",
# 			   "parent": "Case"
#             },
#             {
#                "id": "RejectX",
#                "label": "Reject",
#                "roles": "Manager",
# 			   "parent": "Case"
#             },
#             {
#                "id": "Withdraw",
#                "label": "Withdraw the expense report",
#                "roles": "Employee",
# 			   "parent": "Case"
#             },
#             {
#                "id": "Approve",
#                "label": "Approve",
#                "roles": "Manager",
# 			   "parent": "Case"
#             },
#             {
#                "id": "Payout",
#                "label": "Pay out",
#                "roles": "Finance",
#                "datatype": "int",
# 			   "parent": "Case"
#             }
#          ],
#          "rules": [
#             {
#                "type": "condition",
#                "source": "FilloutExpenseReport",
#                "target": "Approve",
#                "description": "Delay of 2 days",
#                "duration": "P2D"
#             },
#             {
#                "type": "condition",
#                "source": "Approve",
#                "target": "Payout",
#                "description": "Important rule with \"quote\" and 'single quote' in the string Les than < Morten & Co"
#             },
#             {
#                "type": "response",
#                "source": "FilloutExpenseReport",
#                "target": "Payout",
#                "description": "You must payout within a week",
#                "duration": "P7D",
#                "guard": "FilloutExpenseReport@executed"
#             }
#          ]
#       }
#    ]
# }
