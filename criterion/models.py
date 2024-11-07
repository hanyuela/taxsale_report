from django.db import models


class Criterion(models.Model):
    AL = models.BooleanField(default=False)  # Alabama
    AK = models.BooleanField(default=False)  # Alaska
    AZ = models.BooleanField(default=False)  # Arizona
    AR = models.BooleanField(default=False)  # Arkansas
    CA = models.BooleanField(default=False)  # California
    CO = models.BooleanField(default=False)  # Colorado
    CT = models.BooleanField(default=False)  # Connecticut
    DE = models.BooleanField(default=False)  # Delaware
    FL = models.BooleanField(default=False)  # Florida
    GA = models.BooleanField(default=False)  # Georgia
    HI = models.BooleanField(default=False)  # Hawaii
    ID = models.BooleanField(default=False)  # Idaho
    IL = models.BooleanField(default=False)  # Illinois
    IN = models.BooleanField(default=False)  # Indiana
    IA = models.BooleanField(default=False)  # Iowa
    KS = models.BooleanField(default=False)  # Kansas
    KY = models.BooleanField(default=False)  # Kentucky
    LA = models.BooleanField(default=False)  # Louisiana
    ME = models.BooleanField(default=False)  # Maine
    MD = models.BooleanField(default=False)  # Maryland
    MA = models.BooleanField(default=False)  # Massachusetts
    MI = models.BooleanField(default=False)  # Michigan
    MN = models.BooleanField(default=False)  # Minnesota
    MS = models.BooleanField(default=False)  # Mississippi
    MO = models.BooleanField(default=False)  # Missouri
    MT = models.BooleanField(default=False)  # Montana
    NE = models.BooleanField(default=False)  # Nebraska
    NV = models.BooleanField(default=False)  # Nevada
    NJ = models.BooleanField(default=False)  # New Jersey
    NM = models.BooleanField(default=False)  # New Mexico
    NY = models.BooleanField(default=False)  # New York
    NC = models.BooleanField(default=False)  # North Carolina
    ND = models.BooleanField(default=False)  # North Dakota
    OH = models.BooleanField(default=False)  # Ohio
    OK = models.BooleanField(default=False)  # Oklahoma
    OR = models.BooleanField(default=False)  # Oregon
    PA = models.BooleanField(default=False)  # Pennsylvania
    RI = models.BooleanField(default=False)  # Rhode Island
    SC = models.BooleanField(default=False)  # South Carolina
    SD = models.BooleanField(default=False)  # South Dakota
    TN = models.BooleanField(default=False)  # Tennessee
    TX = models.BooleanField(default=False)  # Texas
    UT = models.BooleanField(default=False)  # Utah
    VT = models.BooleanField(default=False)  # Vermont
    VA = models.BooleanField(default=False)  # Virginia
    WA = models.BooleanField(default=False)  # Washington
    WV = models.BooleanField(default=False)  # West Virginia
    WI = models.BooleanField(default=False)  # Wisconsin
    WY = models.BooleanField(default=False)  # Wyoming
    DC = models.BooleanField(default=False)  # Washington, D.C.
    #  New Hampshire has no tax sales


    def __str__(self):
        return f"State Availability Record {self.id}"
