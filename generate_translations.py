#!/usr/bin/env python3
import re

hu_translations = {
    "Register Team": "Csapat regisztrálása",
    "Register a Team": "Csapat regisztrálása",
    "Event": "Esemény",
    "e.g. Brainiacs": "pl. Észbontók",
    "As the team creator, you will become the Team Captain. Only you will be able to invite other players using a unique invite link.": "A csapat létrehozójaként te leszel a Csapatkapitány. Csak te hívhatsz meg más játékosokat az egyedi meghívó link segítségével.",
    "You are already in a team. You must leave your current team first.": "Már tagja vagy egy csapatnak. Előbb el kell hagynod a jelenlegi csapatodat.",
    "A team with this name already exists for this event": "Már létezik ilyen nevű csapat ehhez az eseményhez",
    "Team registered successfully! You are the team captain.": "Csapat sikeresen regisztrálva! Te vagy a csapatkapitány.",
    "This event is no longer active.": "Ez az esemény már nem aktív.",
    "Please log in or register to join the team: %(team)s": "Kérjük, jelentkezz be vagy regisztrálj a csatlakozáshoz: %(team)s",
    "You are already a member of this team.": "Már tagja vagy ennek a csapatnak.",
    "You are already in another team. You can only belong to one team at a time.": "Már egy másik csapat tagja vagy. Egyszerre csak egy csapathoz tartozhatsz.",
    "This team is already full.": "Ez a csapat már megtelt.",
    "You have successfully joined %(team)s!": "Sikeresen csatlakoztál a(z) %(team)s csapathoz!",
    "Only the team captain can remove members.": "Csak a csapatkapitány távolíthat el tagokat.",
    "The captain cannot be removed from the team. Use leave team instead.": "A kapitány nem távolítható el a csapatból. Használd a kilépést.",
    "User is not in this team.": "A felhasználó nem tagja ennek a csapatnak.",
    "Member %(username)s has been removed from the team.": "%(username)s tag el lett távolítva a csapatból.",
    "Only the team captain can regenerate the invite link.": "Csak a csapatkapitány generálhat új meghívó linket.",
    "Invite link has been regenerated.": "A meghívó link sikeresen újragenerálva.",
    "Joining teams is only possible via captain invite link.": "Csapathoz csatlakozni csak a kapitány meghívó linkjével lehet.",
    "You left the team. Leadership has been transferred to %(user)s.": "Elhagytad a csapatot. A vezetés átadva %(user)s számára.",
    "You left and dissolved the team.": "Elhagytad a csapatot, és a csapat feloszlott.",
    "Join & Play": "Csatlakozás & Játék",
    "No active events at the moment. Check back later or browse past quizzes below!": "Jelenleg nincs aktív esemény. Nézz vissza később, vagy böngéssz az alábbi korábbi kvízek között!",
    "Past Quizzes & Events": "Elmúlt Kvízek és Események",
    "Completed": "Lezárult",
    "Ended": "Véget ért",
    "Winner": "Győztes",
    "Leaderboard & Details": "Eredménytábla és Részletek",
    "No past quiz events found.": "Nem találhatók korábbi kvíz események.",
    "Team Leaderboard": "Csapat Ranglista",
    "Captain": "Kapitány",
    "No teams registered yet.": "Még nincs regisztrált csapat.",
    "Your Team & Participation": "A Csapatod és Részvétel",
    "Team Members": "Csapattagok",
    "Team Captain": "Csapatkapitány",
    "You": "Te",
    "Are you sure you want to remove this member?": "Biztosan el szeretnéd távolítani ezt a tagot?",
    "Remove member": "Tag eltávolítása",
    "Remove": "Eltávolítás",
    "Team Invite Link": "Csapat Meghívó Link",
    "Share this link with your teammates. Only you as captain can invite new members.": "Oszd meg ezt a linket a csapattársaiddal. Csak te hívhatsz meg új tagokat csapatkapitányként.",
    "Copy": "Másolás",
    "Copied!": "Másolva!",
    "Regenerate invite link": "Meghívó link újragenerálása",
    "View Your Results": "Eredményeid megtekintése",
    "Start / Continue Quiz": "Kvíz indítása / folytatása",
    "Are you sure you want to leave this team?": "Biztosan el szeretnéd hagyni ezt a csapatot?",
    "You are already in a team (%(team)s) for another event. You can only belong to one team at a time.": "Már tagja vagy a(z) %(team)s csapatnak egy másik eseménynél. Egyszerre csak egy csapathoz tartozhatsz.",
    "Leave current team": "Jelenlegi csapat elhagyása",
    "Ready to play?": "Készen állsz a játékra?",
    "You can register a new team and invite your friends as team captain, or use an invite link sent by your team captain.": "Regisztrálhatsz új csapatot és meghívhatod barátaidat csapatkapitányként, vagy használhatsz egy meghívó linket, amit a csapatkapitányod küldött.",
    "Register a Team (Be Captain)": "Csapat regisztrálása (Legyél Kapitány)",
    "Event is closed for new team registrations.": "Az esemény lezárult az új csapatregisztrációk előtt.",
    "Please log in or register to participate in this quiz event.": "Kérjük, jelentkezz be vagy regisztrálj a részvételhez ebben a kvíz eseményben.",
    "How team membership works": "Hogyan működik a csapatkezelés",
    "Each player can belong to only one team at a time.": "Minden játékos egyszerre csak egy csapathoz tartozhat.",
    "Anyone can create a team and become Team Captain.": "Bárki létrehozhat csapatot és Csapatkapitánnyá válhat.",
    "Only the captain can invite teammates via private invite link.": "Csak a kapitány hívhat meg csapattársakat privát meghívó linken keresztül.",
    "Captains can manage and remove members if needed.": "A kapitányok szükség esetén kezelhetik és eltávolíthatják a tagokat.",
    "pts": "pont",
    "Welcome": "Üdvözlünk",
    "Events": "Események",
    "Quiz Events": "Kvíz Események",
    "Next Generation Interactive Quiz Platform": "Új generációs interaktív kvíz platform",
    "Test Your Knowledge,": "Tedd próbára a tudásod,",
    "Compete in Teams, Win Glory.": "Versenyezz csapatban, szerezz dicsőséget.",
    "Join real-time multi-group quiz championships, form dream teams with captain invite links, solve varied question types, and climb the live leaderboards.": "Csatlakozz valós idejű többcsoportos kvíz bajnokságokhoz, hozz létre álomcsapatot kapitányi meghívóval, oldj meg változatos kérdéseket és hódítsd meg az élő ranglistákat.",
    "Explore Quiz Events": "Kvíz események felfedezése",
    "Create Free Account": "Ingyenes regisztráció",
    "View Leaderboards": "Ranglisták megtekintése",
    "Live Events": "Élő események",
    "Quizzes Created": "Létrehozott kvízek",
    "Teams Competing": "Versenyző csapatok",
    "Why You Will Love Quiz App": "Miért fogod imádni a Quiz App-ot",
    "Built from the ground up for speed, mobile responsiveness, and competitive excitement.": "Alapoktól a sebességre, mobilbarát használatra és a versenyszerű izgalmakra tervezve.",
    "Captain & Team System": "Kapitány- és csapatrendszer",
    "Create your team, receive a unique invite link, and recruit teammates. Captains maintain full control over membership.": "Hozd létre csapatodat, kapj egyedi meghívó linket és toborozz csapattársakat. A kapitányok teljes kontrollal bírnak a tagság felett.",
    "Multi-Group Quizzes": "Többcsoportos kvízek",
    "Solve questions grouped into rounds with page-by-page flow, configurable backtracking rules, and instant answer feedback.": "Válaszolj körökre osztott kérdéscsoportokra laponkénti navigációval, konfigurálható visszalépési szabályokkal és azonnali visszajelzéssel.",
    "Live Scores & Past Archives": "Élő pontok és archívum",
    "Track your standings against other teams in real time and celebrate past champions in our dedicated event archive.": "Kövesd az állást más csapatokkal szemben valós időben, és tekintsd meg a korábbi bajnokokat a dedikált archívumban.",
    "Diverse Question Formats": "Változatos kérdéstípusok",
    "From classic multiple choice and multi-select to open-ended free text with automated or manual review grading.": "A klasszikus feleletválasztóstól és többes jelöléstől a nyílt végű szabadszavas kérdésekig automatikus vagy kézi felülvizsgálattal.",
    "Powerful Admin Suite": "Hatékony adminisztráció",
    "Organizers can easily create custom events, design question sets, reorder rounds, and manually grade open-ended answers.": "A szervezők könnyedén létrehozhatnak egyedi eseményeket, kérdéscsomagokat, átrendezhetik a köröket és pontozhatják a válaszokat.",
    "Fully Mobile & Local": "Teljesen mobilbarát és helyi",
    "Zero external CDN dependencies, ultra-fast loading, fully responsive touch UI, and multilingual support in English and Hungarian.": "Nulla külső CDN függőség, villámgyors betöltés, reszponzív érintőképernyős felület, és többnyelvű (angol és magyar) támogatás.",
    "Featured Live Events": "Kiemelt élő események",
    "Jump straight into active competitions happening right now.": "Csatlakozz közvetlenül az éppen most zajló aktív versenyekhez.",
    "View All Events": "Összes esemény megtekintése",
    "Play Now": "Játék most",
    "Ready to Test Your Skills?": "Készen állsz tesztelni a tudásodat?",
    "Assemble your team, challenge other players, and climb to the top of the leaderboard.": "Állítsd össze a csapatodat, hívd ki a többi játékost, és juss fel a ranglista tetejére.",
    "Browse All Events": "Összes esemény böngészése",
    "Sign Up Now": "Regisztrálj most"
}

def update_po_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    entries = re.split(r'\n(?=msgid )', content)
    new_entries = []
    
    for entry in entries:
        msgid_match = re.search(r'msgid "(.*?)"(?:\n"(.*?)")*', entry)
        if msgid_match:
            full_msgid = ""
            for line in re.findall(r'msgid "(.*?)"|"(.*?)"', entry):
                full_msgid += line[0] or line[1]
                
            if full_msgid in hu_translations:
                trans = hu_translations[full_msgid]
                # Replace msgstr "" or msgstr "..."
                entry = re.sub(r'msgstr "(?:.*?)"(?:\n"(?:.*?)")*', f'msgstr "{trans}"', entry, count=1)
                
        new_entries.append(entry)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_entries))
    print(f"Updated {filepath}")

if __name__ == '__main__':
    update_po_file('app/translations/hu/LC_MESSAGES/messages.po')
