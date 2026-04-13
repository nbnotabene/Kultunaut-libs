-- Migration: Replace arrevent view with eventsArr
-- Version: 005
-- Date: 2026-04-13
--
-- Renames view arrevent → eventsArr and switches to LEFT OUTER JOIN so
-- eventsdata rows without a matching arrsdata row are still returned.
-- All columns from both tables are included, except arrsdata.AinfoNr
-- (already present from eventsdata). Shared column names (created_at,
-- updated_at, is_locked) are disambiguated with event_ / arr_ prefixes.

DROP VIEW IF EXISTS arrevent;

CREATE OR REPLACE VIEW eventsArr AS
    SELECT
        -- eventsdata columns
        e.ArrNr,
        e.AinfoNr,
        e.ArrStart,
        e.extra,
        e.created_at        AS event_created_at,
        e.updated_at        AS event_updated_at,
        e.is_locked         AS event_is_locked,

        -- arrsdata columns (AinfoNr excluded — already in eventsdata)
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
        a.Playdk,
        a.tmdb,
        a.kulthash,
        a.created_at        AS arr_created_at,
        a.updated_at        AS arr_updated_at,
        a.is_locked         AS arr_is_locked

    FROM eventsdata e
    LEFT OUTER JOIN arrsdata a ON e.AinfoNr = a.AinfoNr;
