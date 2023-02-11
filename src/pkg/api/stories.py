from uuid import UUID


STORY_PACKS = {
    UUID("C4139D59-872A-4D15-8CF1-76D34CDF38C6") : "Suzanne et Gaston ",
    UUID("03933BA4-4FBF-475F-9ECC-35EFB4D11DC9") : "Panique aux 6 Royaumes ",
    UUID("22137B29-8646-4335-8069-4A4C9A2D7E89") : "Au Pays des Loups ",
    UUID("29264ADF-5A9F-451A-B1EC-2AE21BBA473C") : "Sur les bancs de l'école ",
    UUID("2F0F3109-BFAE-4E09-91D7-CA0C2643948D") : "Le loup dans tous ses états ",
    UUID("3712AF6D-CF9D-4154-8E98-56821362862A") : "Pandaroux et les Turbo-Héros ",
    UUID("59A710E9-2F7A-4D0C-AB2D-47E8DD2E29B7") : "Pandaroux ",
    UUID("9C836C24-34C4-4CC1-B9E6-D8646C8D9CF1") : "Les Aventures de Zoé -<br> Les 6 Royaumes ",
    UUID("9D9521E5-84AC-4CC8-9B09-8D0AFFB5D68A") : "Suzanne et Gaston fêtent Pâques ",
    UUID("AA0BC5DD-16FA-4362-859C-0DB158139FE6") : "Les bandes a écouter de Yakari ",
    UUID("BF573171-5E5D-4A50-BA89-403277175114") : "En attendant Noël ",
    UUID("D56A4975-417E-4D04-AEB3-21254058B612") : "Oh les pirates ! ",
    UUID("FB2B7DF4-BE3F-4998-83F0-BFBBDA75B9D7") : "A la poursuite des 12 joyaux ",
}

STORY_UNKNOWN = "Unknown story..."

def story_name(story_uuid : UUID):
    if story_uuid in STORY_PACKS:
        return STORY_PACKS[story_uuid]
    return STORY_UNKNOWN