import calendar
import datetime
from abc import ABC, abstractmethod


class _Reader(ABC):

    _path = None
    _usecols = None
    _skiprows = None
    _nrows_max = None
    _df = None

    @classmethod
    def run(cls, path, usecols, skiprows, nrows_max=1e5):
        """Reads file and returns final raw data as pandas dataframe."""
        cls._customize(path, usecols, skiprows, nrows_max)
        cls._read()

    @classmethod
    def run_specific(cls, path, usecols, skiprows, nrows_max=1e5):
        """Parses file and returns final pure data as pandas dataframe.

        Args:
            path: File path.
            usecols: A list of integers representing column numbers of excel table.
                1st integer must be column number of date.
                2 - well name.
                3 - oil production.
                4 - liquid production.
                5 - formation name or bhp.
                Column numeration starts from zero.
            skiprows: Number of rows to skip at the beginning.
            nrows_max: Number of rows to parse.
        """
        cls._customize(path, usecols, skiprows, nrows_max)
        cls._read()
        cls._process()
        return cls._df

    @classmethod
    @abstractmethod
    def _read(cls):
        pass

    @classmethod
    def _customize(cls, path, usecols, skiprows, nrows_max):
        cls._path = path
        cls._usecols = usecols
        cls._skiprows = skiprows
        cls._nrows_max = nrows_max

    @classmethod
    @abstractmethod
    def _process(cls):
        cls._df = cls._df[cls._usecols]
        cls._df.rename(columns={0: 'date'}, inplace=True)
        cls._df['date'] = cls._df['date'].apply(func=cls._convert_date_from_string)
        cls._df.sort_values(by='date', axis='index', ascending=True, inplace=True, ignore_index=True)

    @staticmethod
    def _convert_date_from_string(x):
        if type(x) is not str:
            return x
        format_date = '%m.%Y'
        date = datetime.datetime.strptime(x, format_date)
        day_last = calendar.monthrange(date.year, date.month)[1]  # A last day of the date month.
        date = date.replace(day=day_last)
        return date
