
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB = "bakelit.db"

ALLAPOTOK = ("Kiváló", "Jó", "Rossz")


def init_database():
    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist TEXT NOT NULL,
            album TEXT NOT NULL,
            year INTEGER,
            status TEXT DEFAULT 'Jó'
        )
    """)

    columns = conn.execute(
        "PRAGMA table_info(records)"
    ).fetchall()

    column_names = [column[1] for column in columns]

    if "status" not in column_names:
        conn.execute(
            "ALTER TABLE records ADD COLUMN status TEXT DEFAULT 'Jó'"
        )

    conn.execute("""
        UPDATE records
        SET status = 'Jó'
        WHERE status IS NULL OR status = ''
    """)

    conn.commit()
    conn.close()


def add_record():
    artist = artist_add.get().strip()
    album = album_add.get().strip()
    year = year_add.get().strip()
    status = status_add.get().strip()

    if not artist or not album:
        messagebox.showwarning(
            "Hiányzó adat",
            "Az előadó és az album megadása kötelező."
        )
        return

    if year:
        try:
            year = int(year)
        except ValueError:
            messagebox.showwarning(
                "Hibás év",
                "Az év csak szám lehet."
            )
            return
    else:
        year = None

    if status not in ALLAPOTOK:
        status = "Jó"

    conn = sqlite3.connect(DB)

    conn.execute(
        """
        INSERT INTO records
        (artist, album, year, status)
        VALUES (?, ?, ?, ?)
        """,
        (artist, album, year, status)
    )

    conn.commit()
    conn.close()

    artist_add.delete(0, tk.END)
    album_add.delete(0, tk.END)
    year_add.delete(0, tk.END)
    status_add.set("Jó")

    search()


def delete_record():
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Nincs kiválasztva",
            "Először válassz ki egy lemezt."
        )
        return

    if len(selected) > 1:
        messagebox.showwarning(
            "Több lemez kijelölve",
            "Több lemez van kijelölve. Használd a "
            "'Tömeges törlés' gombot."
        )
        return

    record_id = selected[0]

    if not messagebox.askyesno(
        "Törlés",
        "Biztosan törlöd a kiválasztott lemezt?"
    ):
        return

    conn = sqlite3.connect(DB)

    conn.execute(
        "DELETE FROM records WHERE id = ?",
        (record_id,)
    )

    conn.commit()
    conn.close()

    search()


def bulk_delete():
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Nincs kiválasztva",
            "Jelölj ki legalább egy lemezt."
        )
        return

    count = len(selected)

    if not messagebox.askyesno(
        "Tömeges törlés",
        f"Biztosan törlöd a kijelölt {count} lemezt?"
    ):
        return

    conn = sqlite3.connect(DB)

    for record_id in selected:
        conn.execute(
            "DELETE FROM records WHERE id = ?",
            (record_id,)
        )

    conn.commit()
    conn.close()

    search()


def edit_record():
    selected = table.selection()

    if not selected:
        messagebox.showwarning(
            "Nincs kiválasztva",
            "Jelölj ki egy lemezt a szerkesztéshez."
        )
        return

    if len(selected) > 1:
        messagebox.showwarning(
            "Több lemez kijelölve",
            "Szerkesztéshez csak egy lemez lehet kijelölve."
        )
        return

    record_id = selected[0]

    conn = sqlite3.connect(DB)

    record = conn.execute(
        """
        SELECT artist, album, year, status
        FROM records
        WHERE id = ?
        """,
        (record_id,)
    ).fetchone()

    conn.close()

    if not record:
        messagebox.showwarning(
            "Hiba",
            "A kiválasztott lemez nem található."
        )
        return

    old_artist, old_album, old_year, old_status = record

    window = tk.Toplevel(root)
    window.title("Lemez szerkesztése")
    window.geometry("450x280")
    window.resizable(False, False)

    ttk.Label(
        window,
        text="Előadó"
    ).grid(
        row=0,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    artist_edit = ttk.Entry(
        window,
        width=40
    )

    artist_edit.grid(
        row=0,
        column=1,
        padx=10,
        pady=10
    )

    artist_edit.insert(
        0,
        old_artist
    )

    ttk.Label(
        window,
        text="Album"
    ).grid(
        row=1,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    album_edit = ttk.Entry(
        window,
        width=40
    )

    album_edit.grid(
        row=1,
        column=1,
        padx=10,
        pady=10
    )

    album_edit.insert(
        0,
        old_album
    )

    ttk.Label(
        window,
        text="Év"
    ).grid(
        row=2,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    year_edit = ttk.Entry(
        window,
        width=12
    )

    year_edit.grid(
        row=2,
        column=1,
        padx=10,
        pady=10,
        sticky="w"
    )

    if old_year:
        year_edit.insert(
            0,
            str(old_year)
        )

    ttk.Label(
        window,
        text="Állapot"
    ).grid(
        row=3,
        column=0,
        padx=10,
        pady=10,
        sticky="w"
    )

    status_edit = ttk.Combobox(
        window,
        values=ALLAPOTOK,
        state="readonly",
        width=12
    )

    status_edit.grid(
        row=3,
        column=1,
        padx=10,
        pady=10,
        sticky="w"
    )

    if old_status in ALLAPOTOK:
        status_edit.set(old_status)
    else:
        status_edit.set("Jó")

    def save_edit():

        artist = artist_edit.get().strip()
        album = album_edit.get().strip()
        year = year_edit.get().strip()
        status = status_edit.get().strip()

        if not artist or not album:
            messagebox.showwarning(
                "Hiányzó adat",
                "Az előadó és az album megadása kötelező.",
                parent=window
            )
            return

        if year:
            try:
                year = int(year)
            except ValueError:
                messagebox.showwarning(
                    "Hibás év",
                    "Az év csak szám lehet.",
                    parent=window
                )
                return
        else:
            year = None

        if status not in ALLAPOTOK:
            status = "Jó"

        conn = sqlite3.connect(DB)

        conn.execute(
            """
            UPDATE records
            SET artist = ?,
                album = ?,
                year = ?,
                status = ?
            WHERE id = ?
            """,
            (
                artist,
                album,
                year,
                status,
                record_id
            )
        )

        conn.commit()
        conn.close()

        window.destroy()

        search()

    ttk.Button(
        window,
        text="Mentés",
        command=save_edit
    ).grid(
        row=4,
        column=1,
        padx=10,
        pady=20,
        sticky="w"
    )


def search():
    artist = artist_search.get().strip()
    album = album_search.get().strip()
    year_from = year_from_search.get().strip()
    year_to = year_to_search.get().strip()

    query = """
        SELECT id, artist, album, year, status
        FROM records
        WHERE 1=1
    """

    params = []

    if artist:
        query += " AND artist LIKE ?"
        params.append("%" + artist + "%")

    if album:
        query += " AND album LIKE ?"
        params.append("%" + album + "%")

    if year_from:
        try:
            query += " AND year >= ?"
            params.append(int(year_from))
        except ValueError:
            messagebox.showwarning(
                "Hibás év",
                "Az 'Év-tól' mezőbe számot írj."
            )
            return

    if year_to:
        try:
            query += " AND year <= ?"
            params.append(int(year_to))
        except ValueError:
            messagebox.showwarning(
                "Hibás év",
                "Az 'Év-ig' mezőbe számot írj."
            )
            return

    query += """
        ORDER BY artist COLLATE NOCASE,
                 album COLLATE NOCASE
    """

    conn = sqlite3.connect(DB)

    rows = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    for item in table.get_children():
        table.delete(item)

    for row in rows:
        record_id, artist, album, year, status = row

        table.insert(
            "",
            tk.END,
            iid=str(record_id),
            values=(
                artist,
                album,
                year or "",
                status or "Jó"
            )
        )

    count_label.config(
        text=f"{len(rows)} találat"
    )


def clear_search():
    artist_search.delete(0, tk.END)
    album_search.delete(0, tk.END)
    year_from_search.delete(0, tk.END)
    year_to_search.delete(0, tk.END)

    search()


def bulk_add():
    """
    Tömeges hozzáadás.

    Formátum:
    Előadó | Album | Év | Állapot
    """

    window = tk.Toplevel(root)
    window.title("Tömeges hozzáadás")
    window.geometry("700x500")
    window.minsize(600, 400)

    ttk.Label(
        window,
        text="Tömeges hozzáadás"
    ).pack(pady=(10, 5))

    ttk.Label(
        window,
        text="Egy sor egy lemez. Formátum: Előadó | Album | Év | Állapot"
    ).pack(pady=(0, 10))

    text_box = tk.Text(
        window,
        wrap="none",
        font=("Consolas", 10)
    )

    text_box.pack(
        fill="both",
        expand=True,
        padx=10,
        pady=5
    )

    scrollbar = ttk.Scrollbar(
        window,
        orient="vertical",
        command=text_box.yview
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    text_box.configure(
        yscrollcommand=scrollbar.set
    )

    def import_records():

        content = text_box.get(
            "1.0",
            tk.END
        ).strip()

        if not content:
            messagebox.showwarning(
                "Üres mező",
                "Nincs bemásolt adat."
            )
            return

        lines = content.splitlines()

        conn = sqlite3.connect(DB)

        added = 0
        errors = []

        for line_number, line in enumerate(
            lines,
            start=1
        ):

            line = line.strip()

            if not line:
                continue

            parts = line.split("|")

            if len(parts) < 2:
                errors.append(
                    f"{line_number}. sor: hiányos adat"
                )
                continue

            artist = parts[0].strip()
            album = parts[1].strip()

            year = None

            if len(parts) >= 3:
                year_text = parts[2].strip()

                if year_text:
                    try:
                        year = int(year_text)
                    except ValueError:
                        errors.append(
                            f"{line_number}. sor: hibás év"
                        )
                        continue

            status = "Jó"

            if len(parts) >= 4:
                status_text = parts[3].strip()

                if status_text:
                    status_found = None

                    for valid_status in ALLAPOTOK:
                        if status_text.lower() == valid_status.lower():
                            status_found = valid_status
                            break

                    if status_found is None:
                        errors.append(
                            f"{line_number}. sor: hibás állapot "
                            f"(Kiváló / Jó / Rossz)"
                        )
                        continue

                    status = status_found

            if not artist:
                errors.append(
                    f"{line_number}. sor: hiányzó előadó"
                )
                continue

            if not album:
                errors.append(
                    f"{line_number}. sor: hiányzó album"
                )
                continue

            conn.execute(
                """
                INSERT INTO records
                (artist, album, year, status)
                VALUES (?, ?, ?, ?)
                """,
                (
                    artist,
                    album,
                    year,
                    status
                )
            )

            added += 1

        conn.commit()
        conn.close()

        search()

        if errors:

            error_text = "\n".join(
                errors[:20]
            )

            if len(errors) > 20:
                error_text += (
                    f"\n... és még {len(errors) - 20} hiba."
                )

            messagebox.showwarning(
                "Importálás kész",
                f"Hozzáadva: {added} lemez\n"
                f"Hibás sorok: {len(errors)}\n\n"
                f"{error_text}"
            )

        else:

            messagebox.showinfo(
                "Importálás kész",
                f"Sikeresen hozzáadva: {added} lemez."
            )

        window.destroy()

    ttk.Button(
        window,
        text="Hozzáadás",
        command=import_records
    ).pack(
        pady=10
    )


# -------------------------
# Program
# -------------------------

init_database()

root = tk.Tk()

root.title("Bakelit adatbázis")
root.geometry("900x600")


# Keresés
search_frame = ttk.LabelFrame(
    root,
    text="Keresés"
)

search_frame.pack(
    fill="x",
    padx=10,
    pady=10
)

ttk.Label(
    search_frame,
    text="Előadó / Band"
).grid(
    row=0,
    column=0,
    padx=5,
    pady=5
)

artist_search = ttk.Entry(
    search_frame,
    width=25
)

artist_search.grid(
    row=0,
    column=1,
    padx=5,
    pady=5
)

ttk.Label(
    search_frame,
    text="Album"
).grid(
    row=0,
    column=2,
    padx=5,
    pady=5
)

album_search = ttk.Entry(
    search_frame,
    width=25
)

album_search.grid(
    row=0,
    column=3,
    padx=5,
    pady=5
)

ttk.Label(
    search_frame,
    text="Év-tól"
).grid(
    row=1,
    column=0,
    padx=5,
    pady=5
)

year_from_search = ttk.Entry(
    search_frame,
    width=10
)

year_from_search.grid(
    row=1,
    column=1,
    padx=5,
    pady=5,
    sticky="w"
)

ttk.Label(
    search_frame,
    text="Év-ig"
).grid(
    row=1,
    column=2,
    padx=5,
    pady=5
)

year_to_search = ttk.Entry(
    search_frame,
    width=10
)

year_to_search.grid(
    row=1,
    column=3,
    padx=5,
    pady=5,
    sticky="w"
)

ttk.Button(
    search_frame,
    text="Keresés",
    command=search
).grid(
    row=0,
    column=4,
    rowspan=2,
    padx=15
)

ttk.Button(
    search_frame,
    text="Törlés",
    command=clear_search
).grid(
    row=0,
    column=5,
    rowspan=2,
    padx=5
)


# Táblázat
table_frame = ttk.Frame(root)

table_frame.pack(
    fill="both",
    expand=True,
    padx=10
)

table = ttk.Treeview(
    table_frame,
    columns=(
        "artist",
        "album",
        "year",
        "status"
    ),
    show="headings",
    selectmode="extended"
)

table.heading(
    "artist",
    text="Előadó / Band"
)

table.heading(
    "album",
    text="Album"
)

table.heading(
    "year",
    text="Év"
)

table.heading(
    "status",
    text="Állapot"
)

table.column(
    "artist",
    width=240
)

table.column(
    "album",
    width=360
)

table.column(
    "year",
    width=70
)

table.column(
    "status",
    width=100
)

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=table.yview
)

table.configure(
    yscrollcommand=scrollbar.set
)

table.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)


# Új lemez
add_frame = ttk.LabelFrame(
    root,
    text="Új lemez"
)

add_frame.pack(
    fill="x",
    padx=10,
    pady=10
)

ttk.Label(
    add_frame,
    text="Előadó"
).grid(
    row=0,
    column=0,
    padx=5,
    pady=8
)

artist_add = ttk.Entry(
    add_frame,
    width=20
)

artist_add.grid(
    row=0,
    column=1,
    padx=5,
    pady=8
)

ttk.Label(
    add_frame,
    text="Album"
).grid(
    row=0,
    column=2,
    padx=5,
    pady=8
)

album_add = ttk.Entry(
    add_frame,
    width=25
)

album_add.grid(
    row=0,
    column=3,
    padx=5,
    pady=8
)

ttk.Label(
    add_frame,
    text="Év"
).grid(
    row=0,
    column=4,
    padx=5,
    pady=8
)

year_add = ttk.Entry(
    add_frame,
    width=8
)

year_add.grid(
    row=0,
    column=5,
    padx=5,
    pady=8
)

ttk.Label(
    add_frame,
    text="Állapot"
).grid(
    row=0,
    column=6,
    padx=5,
    pady=8
)

status_add = ttk.Combobox(
    add_frame,
    values=ALLAPOTOK,
    state="readonly",
    width=10
)

status_add.set("Jó")

status_add.grid(
    row=0,
    column=7,
    padx=5,
    pady=8
)

ttk.Button(
    add_frame,
    text="Lemez hozzáadása",
    command=add_record
).grid(
    row=0,
    column=8,
    padx=10
)


# Alsó sor
bottom_frame = ttk.Frame(root)

bottom_frame.pack(
    fill="x",
    padx=10,
    pady=5
)

ttk.Button(
    bottom_frame,
    text="Kiválasztott lemez törlése",
    command=delete_record
).pack(
    side="left"
)

ttk.Button(
    bottom_frame,
    text="Tömeges törlés",
    command=bulk_delete
).pack(
    side="left",
    padx=10
)

ttk.Button(
    bottom_frame,
    text="Szerkesztés",
    command=edit_record
).pack(
    side="left"
)

ttk.Button(
    bottom_frame,
    text="Tömeges hozzáadás",
    command=bulk_add
).pack(
    side="left",
    padx=10
)

count_label = ttk.Label(
    bottom_frame,
    text="0 találat"
)

count_label.pack(
    side="right"
)


# Enter = keresés
root.bind(
    "<Return>",
    lambda event: search()
)


search()

root.mainloop()
