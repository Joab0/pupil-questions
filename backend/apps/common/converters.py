from ulid import ULID


class ULIDConverter:
    regex = r"[0-9A-HJKMNP-TV-Z]{26}"

    def to_python(self, value):
        return ULID.from_str(value)

    def to_url(self, value):
        return str(value)
