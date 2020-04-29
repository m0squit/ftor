class StatisticPlotly(object):

    @classmethod
    def _create_statistics(cls):
        cls._fig = subplots.make_subplots(rows=2,
                                          cols=1,
                                          print_grid=True,
                                          specs=[[{'type': 'xy'}],
                                                 [{'type': 'xy'}]])
        cls._add_diff_rel_prod_oil_well()
        cls._add_diff_prod_oil_well()
        cls._fig.update_layout(width=1500,
                               title=dict(text=f'<b>Statistics on 30 days<b>',
                                          font=dict(size=20)))
        file = str(cls._path / f'statistics')
        pl.io.write_html(cls._fig, f'{file}.html', auto_open=False)

    @classmethod
    def _add_mape(cls):
        trace = go.Bar(x=cls._wells, y=cls._mapes)
        cls._fig.add_trace(trace, row=1, col=1)
        cls._fig.update_xaxes(title_text='well', row=1, col=1)
        cls._fig.update_yaxes(title_text='MAPE, fr', row=1, col=1)

    @classmethod
    def _add_diff_rel_prod_oil_well(cls):
        diff_rel_prod_oil_well = []
        for i in range(30):
            diff_rel_prod_oil = 0
            for j in range(cls._n_zone):
                diff_rel_prod_oil += cls._diffs_rel_rate_oil[j][i]
            diff_rel_prod_oil_well.append(diff_rel_prod_oil / cls._n_zone)

        x = [x for x in range(1, 31)]
        y = diff_rel_prod_oil_well
        trace = go.Bar(x=x, y=y)
        cls._fig.add_trace(trace, row=1, col=1)
        cls._fig.update_xaxes(title_text='day', row=1, col=1)
        cls._fig.update_yaxes(title_text='deviation_rate_oil, fr', row=1, col=1)

    @classmethod
    def _add_diff_prod_oil_well(cls):
        diff_prod_oil_well = []
        for i in range(30):
            diff_prod_oil = 0
            for j in range(cls._n_zone):
                diff_prod_oil += cls._diffs_rate_oil[j][i]
            diff_prod_oil_well.append(diff_prod_oil / cls._n_zone)

        x = [x for x in range(1, 31)]
        y = diff_prod_oil_well
        trace = go.Bar(x=x, y=y)
        cls._fig.add_trace(trace, row=2, col=1)
        cls._fig.update_xaxes(title_text='day', row=2, col=1)
        cls._fig.update_yaxes(title_text='deviation_rate_oil, m3/day', row=2, col=1)
