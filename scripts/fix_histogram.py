path = 'magic-lantern-1300d/src/histogram.c'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = """    else if (RAW_HISTOGRAM_ENABLED)
    {
        MENU_SET_WARNING(MENU_WARN_INFO, "Will use RAW histogram in LiveView and after taking a pic.");
    }
}
#endif"""

replacement = """    else if (RAW_HISTOGRAM_ENABLED)
    {
        MENU_SET_WARNING(MENU_WARN_INFO, "Will use RAW histogram in LiveView and after taking a pic.");
    }
}
#else
MENU_UPDATE_FUNC(raw_histo_update) {}
#endif"""

if target in text:
    text = text.replace(target, replacement, 1)
elif target.replace('\n', '\r\n') in text:
    text = text.replace(target.replace('\n', '\r\n'), replacement.replace('\n', '\r\n'), 1)
else:
    print('Target not found in histogram.c')

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)
print('histogram.c updated successfully!')
