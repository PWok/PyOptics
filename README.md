A very simple Python optics library

# Description/Opis Projektu:
## EN:
 *maybe someday...*
## PL 🇵🇱
Bardzo prosta biblioteka optyczna 2D do Pythona.
Składa się z dwóch podmodułów:
- moduł `optics2d` - moduł odpowiadający za przeprowadzanie symulacji
- moduł `renderer` - **bardzo** prosty renderer napisany przy użyciu biblioteki `pygame`

Symulacja polega na *ray tracingu* (technicznie rzecz biorąc...) z ograniczoną liczbą odbić (możliwą do skonfigurowania). Dostępne obiekty optyczne uwzględniają lustra płaskie i sferyczne o dowolnej ogniskowej oraz soczewki.

Do symulacji dołączony jest prosty interfejs graficzny napisany przy użyciu biblioteki `pygame`, ale hierarchia klas została zaprojektowana w sposób, który powinien umożliwiać napisanie własnego renderera bez większych problemów. 


### Instalacja:
#### Sposób 1) Ręcznie:
- sklonuj repo za pomocą `git clone`
- pobierz potrzebne biblioteki (`pygame`, `numpy`)

#### Sposób 2) Przy użyciu pip: 
- `pip install git+https://github.com/PWok/pyoptics`

Jeżeli chcesz zaistalować w trybie edytowalnym sklonuj repo przy pomocy `git clone` i w tym samym folderze uruchom komendę
```bash
pip install --editable .
```
(może nie działać na Windowsie)

### Wymagania:
- pygame
- numpy
    
### Instrukcja obsługi:
uruchom `python3 ./pyoptics -h`, aby zobaczyć help menu
W przypadku otrzymania błędu spróbuj zamaist tego uruchomić `python3 -m pyoptics -h`


Pliki konfiguracyjne:
    Jeżeli chcesz w prosty sposób uruchomić symulację możesz wykorzystać plik konfiguracyjny, na przykład:
```
# Big mirror
F, -0.2, 2.5,   0, 1
S, 0.8,  2.51,  0, 2, 0.5
E, 0,    2.5,   0


# Small mirror with big curvature
F, -0.1, 0.5,   0, 1
S, 0.4,  0.51,  0, 1, 0.25
E, 0,    0.5,   0


# small mirror
F, -0.2, -1.5,  0, 1
S, 0.8,  -1.51, 0, 1, 0.5
E, 0,    -1.5,  0
```

Linijki zaczynające się od `#` to komentarze. `F` to zwierciadła płaskie (`FlatMirror`), `S` -- zwierciadła sferyczne (`SphericalMirror`), a `R` lub `E` -- emitery światła laserowego (`RayEmitter`). Kolejne liczby odpowiadają kolejno współrzędnym `x` oraz `y`, i obrotowi. W przypadku luster dodatkowo dochodzi rozmiar, a dla luster sferycznych również długość ogniskowej.  


Przy otwartym edytorze możliwa jest edycja symulacji "na żywo". Można przeciągać myszką pojedyncze elementy optyczne oraz emitery promieni, oraz obracać je za pomocą kółka myszy. Ponadto można dodawać nowe poprzez naciśnięcie odpowiednich klawiszy na klawiaturze -- `f` dla zwierciadła płaskiego, `s` dla sferycznego, a `e` dla emitera. Przyciśnięcie klawisza `r` resetuje symulację do wczytanego stanu z pliku konfiguracyjnego. Wymuszenie wykonania kolejnego kroku symulacji możemy wykonać poprzez przyciśnięcie **spacji**. Niestety na tą chwilę skalowanie obiektów z poziomu interfejsu graficznego nie jest możliwe.

### Przykładowe pliki konfiguracyjne zawarte są w folderze `examples`
