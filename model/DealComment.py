import settings


class DealComment:
    __slots__ = ['lieder_ticket', 'reason']

    lieder_ticket: int
    reason: str
    SEPARATOR = '-'

    def __init__(self):
        self.lieder_ticket = -1
        self.reason = ''

    @staticmethod
    def is_valid_string(string: str):
        if len(string) > 0:
            sliced = string.split(DealComment.SEPARATOR)
            if len(sliced) == 2:
                if sliced[1] not in settings.reasons_code:
                    return False
                try:
                    ticket = int(sliced[0])
                    if ticket < 0:
                        return False
                except ValueError:
                    return False
            else:
                return False
        return True

    def string(self):
        return f'{self.lieder_ticket}' + DealComment.SEPARATOR + f'{self.reason}'

    def obj(self):
        return {'lieder_ticket': self.lieder_ticket, 'reason': self.reason}

    def set_from_string(self, string: str):
        if DealComment.SEPARATOR in string:
            split_str = string.split(DealComment.SEPARATOR)
            lid_str = split_str[0]
            cause = split_str[1]
        elif len(string) > 0:
            lid_str = string
            cause = ''
        else:
            lid_str = '-1'
            cause = ''
        try:
            self.lieder_ticket = int(lid_str)
            self.reason = cause
        except ValueError:
            self.lieder_ticket = -1
            self.reason = ''
        return self

    def set_from_ticket(self, ticket: int):
        self.lieder_ticket = ticket
        self.reason = ''
