# pyoptics

## optics2d
submoduł odpowiedzialny za przeprowadzanie symulacji.

### <span style="font-size: 75%">*`pyoptics.optics2d.`</span>*<span style="font-size: 120%">**`Optic`**</span>
Bazowa klasa abstrakcyjna dla wszystkich elementów optycznych
> 
> 
> #### <span style="font-size: 75%">*pyoptics.optics2d.Optic.</span>*<span style="font-size: 120%">**location**</span>:
> Położenie elementu optycznego.
> 
> #### <span style="font-size: 75%">*pyoptics.optics2d.Optic.</span>*<span style="font-size: 120%">**rotation**</span>:
> Rotacja elementu optycznego.
> 
> #### <span style="font-size: 75%">*pyoptics.optics2d.Optic.</span>*<span style="font-size: 120%">**scale**</span>:
> Skala elementu optycznego.

> #### <span style="font-size: 75%">*pyoptics.optics2d.Optic.</span>*<span style="font-size: 120%">**get_bounce(**</span>ray<span style="font-size: 120%">**)**</span>:
> Zwróć `None`, jeżeli otrzymany promień nie jest na torze kolizyjnym z tym elementem optycznym. W przeciwnym przypadku zwróć punkt odbicia oraz nowy kierunek padania światła.

### <span style="font-size: 75%">*`pyoptics.optics2d.`</span>*<span style="font-size: 120%">**`FlatMirror(Optic)`**</span>
Konkretyzacja klasy `Optic`. Symuluje zwierciadło płaskie.

### <span style="font-size: 75%">*`pyoptics.optics2d.`</span>*<span style="font-size: 120%">**`SphericalMirror(Optic)`**</span>
Konkretyzacja klasy `Optic`. Symuluje zwierciadło sferyczne.
> #### <span style="font-size: 75%">*pyoptics.optics2d.SphericalMirror.</span>*<span style="font-size: 120%">**focal**</span>:
> Ogniskowa zwierciadła

### <span style="font-size: 75%">*`pyoptics.optics2d.`</span>*<span style="font-size: 120%">**`RayEmitter`**</span>
Emiter światła laserowego
> #### <span style="font-size: 75%">*pyoptics.optics2d.RayEmitter.</span>*<span style="font-size: 120%">**location**</span>:
> Położenie elementu.
> 
> #### <span style="font-size: 75%">*pyoptics.optics2d.RayEmitter.</span>*<span style="font-size: 120%">**rotation**</span>:
> Rotacja elementu.
> 
> #### <span style="font-size: 75%">*pyoptics.optics2d.RayEmitter.</span>*<span style="font-size: 120%">**current_ray_location**</span>:
> Położenie ostatniego miejsca, w którym światło lasera zmieniło kierunek.
> #### <span style="font-size: 75%">*pyoptics.optics2d.RayEmitter.</span>*<span style="font-size: 120%">**last_bounce_direction**</span>:
> Ostatni kierunek w którym podróżowało światło.
> #### <span style="font-size: 75%">*pyoptics.optics2d.RayEmitter.</span>*<span style="font-size: 120%">**bounce_locations**</span>:
> Lista wszystkich punktów w których światło lasera zmieniło kierunek.

> #### <span style="font-size: 75%">*pyoptics.optics2d.RayEmitter.</span>*<span style="font-size: 120%">**reset()**</span>:
> Opróżnij listę `bounce_locations`, ustaw `current_ray_location` i `last_bounce_direction` na odpowiednio `location` i `rotation`


### <span style="font-size: 75%">*`pyoptics.optics2d.`</span>*<span style="font-size: 120%">**`OpticSystem`**</span>
Agreguje emitery światła laserowego i elementy optyczne w system oraz przeprowadza symulację.
> #### <span style="font-size: 75%">*pyoptics.optics2d.OpticSystem.</span>*<span style="font-size: 120%">**rays**</span>:
> Lista wszystkich emiterów światła w tym systemie
> #### <span style="font-size: 75%">*pyoptics.optics2d.OpticSystem.</span>*<span style="font-size: 120%">**optics**</span>:
> Lista wszystkich elementów optycznych w tym systemie

> #### <span style="font-size: 75%">*pyoptics.optics2d.OpticSystem.</span>*<span style="font-size: 120%">**step()**</span>:
> Wykonaj jeden krok symulacji.
> #### <span style="font-size: 75%">*pyoptics.optics2d.OpticSystem.</span>*<span style="font-size: 120%">**add(obj)**</span>:
> Dodaj `obj` odpowiednio do `self.rays` lub `self.optics`
> #### <span style="font-size: 75%">*pyoptics.optics2d.OpticSystem.</span>*<span style="font-size: 120%">**reset()**</span>:
> Wywołaj `.reset()` na wszystkich elementach pola `self.rays`

&nbsp;

## renderer
Prosty renderer napisany przy użyciu biblioteki `pygame`

### <span style="font-size: 75%">*`pyoptics.renderer.`</span>*<span style="font-size: 120%">**`RenderScene`**</span>
Scena renderera.
> #### <span style="font-size: 75%">*pyoptics.renderer.RenderScene.</span>*<span style="font-size: 120%">**system**</span>:
> instancja `optics2d.OpticSystem`, wynik symulacji której jest renderowany
> #### <span style="font-size: 75%">*pyoptics.renderer.RenderScene.</span>*<span style="font-size: 120%">**object_renderers**</span>:
> Lista wszystkich rendererów należacych do tej sceny
> #### <span style="font-size: 75%">*pyoptics.renderer.RenderScene.</span>*<span style="font-size: 120%">**scr**</span>:
> Ekran `pygame` na którym scena będzie wyświetlana 

> #### <span style="font-size: 75%">*pyoptics.renderer.RenderScene.</span>*<span style="font-size: 120%">**reset()**</span>:
> Wywołaj `.reset()` na systemie
> #### <span style="font-size: 75%">*pyoptics.renderer.RenderScene.</span>*<span style="font-size: 120%">**add()**</span>:
> Dodaj `Optic` lub `RayEmitter` do sceny i systemu
> #### <span style="font-size: 75%">*pyoptics.renderer.RenderScene.</span>*<span style="font-size: 120%">**step()**</span>:
> Wykonaj i wyświetl kolejny krok symulacji
> #### <span style="font-size: 75%">*pyoptics.renderer.RenderScene.</span>*<span style="font-size: 120%">**run([steps])**</span>:
> Uruchom `steps` kroków symulacji. Jeżeli żadna wartości nie zostanie podana wykonaj domyślną ilość kroków.


### <span style="font-size: 75%">*`pyoptics.renderer.`</span>*<span style="font-size: 120%">**`Renderable`**</span>
Klasa abstrakcyjna dla renderowalnych elementów sceny. 
> #### <span style="font-size: 75%">*pyoptics.renderer.Renderable.</span>*<span style="font-size: 120%">**color**</span>
> #### <span style="font-size: 75%">*pyoptics.renderer.Renderable.</span>*<span style="font-size: 120%">**linewidth**</span>
> kolor i szerokość lini renderowania
> #### <span style="font-size: 75%">*pyoptics.renderer.Renderable.</span>*<span style="font-size: 120%">**obj**</span>
> instancja `Optic` bądź `RayEmitter` (zależnie od konkretyzacji), której rendererem jest ten obiekt.

> #### <span style="font-size: 75%">*pyoptics.renderer.Renderable.</span>*<span style="font-size: 120%">**render(scene)**</span>:
> Wyświetl się na ekranie przetrzymywanym przez przekazany obiekt sceny.
> #### <span style="font-size: 75%">*pyoptics.renderer.Renderable.</span>*<span style="font-size: 120%">**render(mouse_loc)**</span>:
> Sprawdź, czy podane koordynaty myszy znajdują się nad tym obiektem 

### <span style="font-size: 75%">*`pyoptics.renderer.`</span>*<span style="font-size: 120%">**`RenderFlat`**</span>:
### <span style="font-size: 75%">*`pyoptics.renderer.`</span>*<span style="font-size: 120%">**`RenderSpherical`**</span>:
### <span style="font-size: 75%">*`pyoptics.renderer.`</span>*<span style="font-size: 120%">**`RenderRay`**</span>:
Róźne konkretyzacje klasy `Renderable`
