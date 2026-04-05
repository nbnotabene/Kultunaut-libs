-- Migration: Create eventsdata and arrsdata tables with Kultunaut column names
-- Version: 002
-- Date: 2026-04-05
--
-- eventsdata: one row per event occurrence (unique by ArrNr)
-- arrsdata:   one row per unique arrangement/film (unique by AinfoNr)
--             holds arrangement-level metadata + TMDB JSON blob

CREATE TABLE IF NOT EXISTS arrsdata (
    AinfoNr         BIGINT          NOT NULL,
    ArrGenre        VARCHAR(50)     NULL,
    ArrKunstner     VARCHAR(255)    NOT NULL,
    ArrBeskrivelse  TEXT            NULL,
    StedNavn        VARCHAR(100)    NULL,
    ArrLangBeskriv  TEXT            NULL,
    ArrUGenre       VARCHAR(100)    NULL,
    BilledeUrl      VARCHAR(500)    NULL,
    Filmvurdering   VARCHAR(20)     NULL,
    Nautanb         TEXT            NULL,
    Nautanmeld      TEXT            NULL,
    Playdk          TEXT            NULL,
    tmdb            JSON        NULL COMMENT 'TMDB API JSON blob',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (AinfoNr),
    INDEX idx_arrsdata_genre (ArrGenre),
    INDEX idx_arrsdata_ugenre (ArrUGenre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ArrStart combines Startdato (DATE) and ArrTidspunkt (e.g. "kl. 19:45") into one DATETIME
CREATE TABLE IF NOT EXISTS eventsdata (
    ArrNr           BIGINT          NOT NULL,
    AinfoNr         BIGINT          NOT NULL,
    ArrStart        DATETIME        NOT NULL COMMENT 'Startdato + ArrTidspunkt combined',
    kulthash        VARCHAR(32)     NULL COMMENT 'MD5 of source data, used for change detection',
    created_at      DATETIME        DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    extra           JSON            NULL COMMENT 'Additional event-level data not in arrsdata',
    PRIMARY KEY (ArrNr),
    INDEX idx_eventsdata_ainfon (AinfoNr),
    INDEX idx_eventsdata_arrstart (ArrStart),
    CONSTRAINT fk_eventsdata_arrsdata
        FOREIGN KEY (AinfoNr) REFERENCES arrsdata (AinfoNr)
        ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE OR REPLACE VIEW arrevent AS
    SELECT
        e.ArrNr,
        e.ArrStart,
        e.AinfoNr,
        e.extra,
        a.ArrGenre,
        a.ArrKunstner,
        a.ArrBeskrivelse,
        a.StedNavn,
        a.ArrLangBeskriv,
        a.ArrUGenre,
        a.BilledeUrl,
        a.Filmvurdering,
        a.Nautanb,
        a.Nautanmeld,
        a.Playdk

    FROM eventsdata e
    JOIN arrsdata a USING (AinfoNr);
