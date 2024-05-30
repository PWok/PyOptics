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