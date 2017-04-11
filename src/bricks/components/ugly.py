class DatePicker(Component):
    class Meta:
        requires = ['jquery', 'jquery-ui']

    def __init__(self, date=None):
        super().__init__()
        self.date = date or datetime.date.today()

    def render(self, **kwargs):
        date = self.date
        return '<input type="date" class="date-picker">%s/%s/%s</input>' % (
            date.day, date.month, date.year)


with capture_assets() as mgm:
    dp = DatePicker()
    print(dp)

print(DatePicker._meta.requires)
print(mgm.render_js())
print(mgm.resolve_dependencies())