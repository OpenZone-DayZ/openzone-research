# packaging

What a published `@Mod` folder needs besides the packed pbo. The `@Mod` folders are build
output and are not in git; `package.ps1` assembles them after `mod_build`.

```
packaging/<Mod>/mod.cpp     the name, author, version and description DayZ shows in
                            the launcher and the mod list
packaging/<Mod>/meta.cpp    the Workshop item id, once the item exists -- without it the
                            next upload CREATES a second item instead of updating
packaging/<Mod>.workshop.bbcode
                            the Workshop listing, English and Ukrainian in one field
packaging/<Mod>.workshop.png
                            the preview image the item's page shows, 1024x512
```

Publishing, in order: `mod_build` (packs and signs) -> `.\package.ps1` (puts the rest in
place; `-Check` only reports) -> `workshop_publish("<Mod>")` from the `dayz` MCP.
