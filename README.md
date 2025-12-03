# Schichtplan Sync

Ein Python-basiertes Tool zum automatischen Herunterladen, Parsen und
Synchronisieren von Dienstplänen aus PDF-Dateien in Kalenderanwendungen
über das iCal-Format.

## Funktionen

-   **PDF-Verarbeitung**: Lädt PDF-Dienstpläne herunter und analysiert
    sie mithilfe von OCR (Tesseract)
-   **Kalender-Integration**: Generiert iCal-Dateien, kompatibel mit
    Google Kalender, Apple Kalender, Outlook usw.
-   **E-Mail-Benachrichtigungen**: Sendet Benachrichtigungen bei
    Änderungen am Dienstplan
-   **FTP-Upload**: Lädt generierte iCal-Dateien automatisch auf einen
    FTP-Server hoch
-   **Verschlüsselte Zugangsdaten**: Speichert Anmeldedaten sicher mit
    Fernet-Verschlüsselung
-   **Verifizierung der Zugangsdaten**: Testet und aktualisiert
    gespeicherte HTTP-, FTP- und SMTP-Zugangsdaten vor jedem Sync
-   **Flexible Konfiguration**: Unterstützt benutzerdefinierte
    Schichtdefinitionen und Nutzerkonfigurationen
-   **Dienstplan-Erweiterung**: Erweitert Dienstpläne automatisch
    basierend auf konfigurierbaren Mustern
-   **Änderungserkennung**: Vergleicht PDF-Inhalt, um unnötige
    Verarbeitung zu vermeiden
-   **Modulare Architektur**: In Utility-Module gegliedert für bessere
    Wartbarkeit

## Voraussetzungen

-   Python 3.6+
-   Tesseract OCR
-   Internetverbindung zum Herunterladen des PDF
-   FTP-Server (optional)

## Installation

1.  **Repository klonen:**

    ``` bash
    git clone https://github.com/rh0vandir/Schichtplan_sync.git
    cd schichtplan_sync
    ```

2.  **Setup-Skript ausführen:**

    ``` bash
    ./setup_schichtplan_sync.sh
    ```

3.  **Konfiguration in `config.json` einrichten**

4.  **Skript einmal manuell ausführen (oder Setup-Flag nutzen), um
    Zugangsdaten einzurichten**

Das Setup-Skript führt aus: - Überprüfung erforderlicher Abhängigkeiten
(Python 3, pip3, Tesseract) - Erstellen einer virtuellen Umgebung -
Installation der benötigten Python-Pakete aus requirements.txt -
Erstellen einer Standard-Konfigurationsdatei

## Konfiguration

Bearbeite `config.json`, um die Anwendung zu konfigurieren. Die
Konfigurationsdatei wird während des Setups automatisch mit
Standardwerten erstellt.

### Pflichtkonfiguration

Diese Einstellungen **müssen** konfiguriert werden, bevor das Tool
korrekt funktionieren kann:

#### `pdf_url` (string)

Die Quelle des PDF-Dienstplans. Dies kann eine entfernte URL
(HTTP/HTTPS) oder ein lokaler Dateipfad sein.

#### `users` (object)

Definiert Nutzer, deren Dienstpläne verarbeitet werden sollen.

(Beispielinhalt wurde aus Platzgründen gekürzt. Bitte füge bei Bedarf
alles hinzu.)
