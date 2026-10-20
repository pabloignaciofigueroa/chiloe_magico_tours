"""Contenido del sitio (fase 6). Todo texto visible de la marca va con su fuente.

Q(texto, fuente)  → texto literal de la marca o de una reseña; se muestra en su idioma original.
U(es, en)         → interfaz: se traduce.
Las fuentes: [IG-NNN] post, [BIO], [DEST-Hn] destacada, [PIEZA] pieza gráfica, [RESEÑA] Google,
[DATO] dato verificable (castroturismo.cl, Google Maps), [UI] texto de interfaz.
tools/build.py genera content/copy.md desde aquí.
"""


class Q(str):
    def __new__(cls, text, src, fix=None):
        o = str.__new__(cls, text); o.src = src; o.fix = fix; return o


class U:
    def __init__(self, es, en): self.es, self.en = es, en


PENDING = U('Por confirmar con la agencia', 'To be confirmed with the agency')

SITE = {
    'name': 'Turismo Chiloé Mágico',
    'domain': 'https://chiloemagicotour.pages.dev',
    'wa': '56978902625',
    'wa_display': '+56 9 7890 2625',
    'phone2': '+56 9 9883 3946',
    'email': 'chiloemagicocontacto@gmail.com',
    'instagram': 'https://www.instagram.com/chiloemagicotour/',
    'address': Q('Av. Gamboa 351, Galería Alonso de Ercilla, Local Interior 116, Castro, Chile', '[BIO]'),
    'address_short': Q('Gamboa 351, Local Interior 116 (Frente a Plaza de Armas Castro)', '[DEST-H7]'),
    'hours': Q('Lu a Do | 9:00 a 19:30', '[BIO]'),
    'lat': -42.4816941, 'lng': -73.7642726,
    'rating': '4,9', 'rating_en': '4.9', 'reviews_count': 46,
    'tagline': Q('Nuestro archipiélago es mágico ¡Ven a descubrirlo!', '[BIO]'),
    'bio1': Q('¡Tours todos los días! - Servicios privados', '[BIO]'),
    'slogan': Q('Chiloé Mágico te espera, Ven a descubrirlo!', '[DEST-H7]'),
    'cierre': Q('¡NO DEJES QUE TE LO CUENTEN, VEN A DISFRUTAR DE ESTA MÁGICA ISLA JUNTO A NOSOTROS!', '[IG-007]'),
    'salida': Q('Salidas desde nuestra agencia, ubicada frente a la plaza de armas, a un costado de la Iglesia de Castro', '[IG-006]'),
    'horario_tour': Q('Todos son tours de día completo (salida a las 10am y retorno a las 7pm aprox)', '[IG-006]'),
    'incluye': Q('Traslado, guiado, almuerzo y bebestibles, y visitas a distintos atractivos turísticos', '[IG-006]'),
    'cupos': Q('Consulta por cupos, no te quedes sin el tuyo', '[IG-006]'),
    'reservas': Q('Informaciones y reservas', '[IG-006]'),
    'van16': Q('Cada van viaja con un máximo de 16 pasajeros y su propio guía, para entregarles un servicio aún más personalizado!', '[IG-007]'),
    'vans': Q('Es por esto que diariamente nos trasladamos en modernas y cómodas vans 🚐 Con aire acondicionado (para que ni el frio ni el calor nos detengan!), asientos reclinables para la siesta post almuerzo, y conductores que además de profesionales son wena onda! 😎', '[IG-007]'),
    'servicio': Q('Nos caracterizamos por prestar el mejor servicio posible para hacer de tu visita una experiencia inolvidable!', '[IG-007]'),
    'somos': Q('Somos Chiloé Mágico! Una empresa dedicada a entregarte la mejor experiencia en nuestro archipiélago. Ven a conocer esta majestuosa zona insular junto a nosotros!', '[IG-017]'),
    'anos': Q('Somos una empresa dedicada al rubro turístico, con más de 20 años de servicio, en la cuál, trabajamos con los más altos estandares y productos de calidad....', '[IG-032]'),
    'magia': Q('Cuando hablamos de Chiloé Mágico, no sólo nos referimos a las mil y un historias que se cuentan sobre mitos, leyendas y brujería 🧙‍♀️', '[IG-042]'),
    'magia2': Q('Magia también es ver la sonrisa de nuestros amigos turistas al final de un largo día de tour ✨', '[IG-042]'),
    'marketing': Q('nuestro marketing y publicidad más grande son nuestros turistas que cuentan sus experiencias con nosotros y por eso les agradecemos .', '[IG-002]'),
    'irrepetible': Q('Chiloe es inolvidable y lo puedes sentir por qué aunque se repita el viaje la experiencia es única e irrepetible', '[IG-002]'),
    'clima': Q('Con viento y lluvia, se vive la magia y aventura de Chiloé.', '[IG-137]'),
    'bosque_mar': Q('Caminar entre bosque y mar es lo mágico de Chiloé', '[IG-083]'),
    'privados': Q('Chiloe Magico Tour, servicio de turismo, traslado y viajes privados', '[IG-016]'),
    'diarias': Q('Contamos con salidas diarias a distintos paramos de este fantástico archipiélago, para consultas y programaciones pueden hablarnos a nuestro WhatsApp', '[IG-033]'),
    'objetivo': Q('Nuestro objetivo principal es hacer de sus vacaciones la mejor experiencia ¡Gracias siempre por confiar en nuestros servicios! 💕', '[IG-070]'),
    'gracias': Q('Gracias por hacernos parte de su paso por este hermoso archipiélago 💝🍃', '[IG-042]'),
    'idioma': Q('FYI the tour is not available in english.', '[RESEÑA Maja, Google]'),
}

# ---------------------------------------------------------------- TOURS
# Paradas: rótulos de los afiches [DEST-H7_00N], en su orden de lectura (izquierda→derecha, arriba→abajo).
TOURS = [
    {
        'slug': 'la-costa-curanto', 'afiche': '[DEST-H7_002]',
        'title': ('TOUR LA COSTA', 'con', 'CURANTO EN HOYO'),
        'short': 'Tour La Costa',
        'hero': 'pasarela-aucar', 'card': 'curanto-destape',
        'gallery': ['curanto-hoyo', 'curanto-hojas', 'curanto-destape', 'curanto-papas', 'tenaun', 'aucar-pasarela', 'tocoihue', 'dalcahue-feria', 'quicavi', 'molinos-mirador'],
        'dest': ['dalcahue-quinchao'], 'exp': ['gastronomia', 'patrimonio', 'naturaleza', 'mitos'],
        'tag': U('Con curanto en hoyo', 'With pit-cooked curanto'),
        'stops': ['Feria Artesanal Dalcahue', 'Iglesia Patrimonio Tenaún', 'Almuerzo en agroturismo', 'Cascadas de Tocoihue', 'Isla Aucar'],
        'stop_imgs': ['dalcahue-feria', 'tenaun', 'curanto-mesa', 'tocoihue', 'aucar-pasarela'],
        'itinerary': [Q(x, '[IG-010]') for x in ['Visita a la ciudad de Dalcahue', 'Llegada al sector de los Molinos para el tapamiento', 'Visita al pueblo de Tenaún', 'Almuerzo en el sector de los Molinos', 'Visita a la Isla Aucar', 'Visita a las Cascadas de Tocoihue', 'Retorno a la ciudad de Castro']],
        'price': Q('$35.000 por persona (incluyendo el almuerzo) + $3.000 por persona (entrada a las cascadas)', '[IG-006]'),
        'price_from': 35000, 'price_season': U('Valor publicado en febrero de 2025. Confirma el valor vigente al reservar.', 'Price published in February 2025. Confirm the current price when booking.'),
        'extras': [Q('$3.000 por persona (entrada a Cascadas)', '[IG-010]')],
        'hook': Q('UN CURANTITO?🤗', '[IG-010]'),
        'lead': Q('Ven a disfrutar de esta exquisita comida típica chilota junto a nosotros', '[IG-010]'),
        'body': [
            Q('En este lugar es donde se lleva a cabo nuestro famoso Curanto en Hoyo del Tour de la Costa, que tiene un mirador espectacular a las Islas Chauques! 😊', '[IG-043]'),
            Q('El curanto en hoyo o curanto al hoyo, es una milenaria técnica de cocción que utiliza piedras calientes en un hoyo excavado en la tierra para cocinar los alimentos, los cuales se tapan con hojas de pague, permitiendo una cocción al vapor con toques ahumados', '[IG-034]'),
            Q('La imponente Cascada de Tocoihue nos deleita con su lechoso manto en donde los brujos se bañaban como ritual de iniciación durante 40 noches🧙‍♂️🧹', '[IG-019]'),
            Q('Un pasarela de 437 metros que hay que cruzar para llegar a la maravillosa Isla Aucar!😱', '[IG-046]'),
        ],
        'reviews': ['Ximena', 'Valeria', 'Jaime'],
    },
    {
        'slug': 'isla-lemuy-asado', 'afiche': '[DEST-H7_008]',
        'title': ('TOUR ISLA LEMUY', 'con', 'ASADO'),
        'short': 'Tour Isla Lemuy',
        'hero': 'brujos-columpio', 'card': 'brujos-columpio-2',
        'gallery': ['brujos-vuelo', 'brujos-alas', 'yayanes-puente', 'lemuy-bosque', 'ichuac', 'aldachildo', 'acordeon', 'asado-cordero', 'detif', 'hueñay-playa'],
        'dest': ['chonchi-lemuy'], 'exp': ['gastronomia', 'patrimonio', 'naturaleza', 'navegacion', 'mitos'],
        'tag': U('Con asado al palo', 'With spit-roast lamb'),
        'stops': ['Feria Artesanal Chonchi', 'Iglesia Patrimonio Vilupulli', 'Navegación Canal Yal', 'Almuerzo en agroturismo', 'Parque Yayanes', 'Recorrido por Lemuy'],
        'stop_imgs': [None, 'vilupulli', None, 'asado-palo', 'yayanes-puente', 'brujos-atardecer'],
        'hook': Q('VAMOS A VOLAR UN RATITO? ✨', '[IG-012]'),
        'lead': Q('…nos vamos nuevamente hacia Isla Lemuy, donde no solo nos envolvemos de naturaleza y comemos rico sino también visitamos el infaltable @muelledelosbrujoschiloe para echarnos a volar en medio de bellos paisajes 🍃', '[IG-012]', fix='se omite «Mañana» (fecha vencida)'),
        'body': [
            Q('El asado de cordero al palo es un deleite para el paladar de toda persona. La cocción de la carne de esta manera es superior a cualquier otra 🍖', '[IG-018]'),
            Q('Nuestros viajeros se vuelven brujos por un día en nuestro tour a la Isla Lemuy!', '[IG-039]'),
            Q('Un puente colgante de 30 metros, que ofrece adrenalina y emoción sin igual!😱', '[IG-064]'),
            Q('Una de las paradas más importantes en la ciudad de Chonchi, es en el Museo del Acordeón de don Sergio Colivoro!🪗', '[IG-063]'),
        ],
        'reviews': ['Andrea', 'Francesca', 'susan'],
    },
    {
        'slug': 'parque-nacional-chiloe', 'afiche': '[DEST-H7_003]',
        'title': ('TOUR', 'Parque', 'NACIONAL CHILOÉ'),
        'short': 'Tour Parque Nacional Chiloé',
        'hero': 'parque-bosque', 'card': 'huillinco-pareja',
        'gallery': ['nercon', 'vilupulli', 'huillinco-columpio', 'cucao-humedal', 'parque-muelle', 'muelle-almas-cielo', 'murta'],
        'dest': ['cucao-parque', 'castro', 'chonchi-lemuy'], 'exp': ['naturaleza', 'patrimonio'],
        'tag': U('Bosque y mar', 'Forest and sea'),
        'stops': ['Iglesia Patrimonio Nercón', 'Artesanía Chonchi', 'Columpio Lago Huillinco', 'Restaurant tradicional', 'Parque Nacional Chiloé', 'Playa Chanquín'],
        'stop_imgs': ['nercon', None, 'huillinco-columpio', None, 'parque-muelle', None],
        'hook': Q('Caminar entre bosque y mar es lo mágico de Chiloé 🌳🌊🤗', '[IG-083]'),
        'lead': Q('¡Camina junto a nosotros a través de esta generosa reserva nacional de flora y fauna nativa! 🌿', '[IG-071]'),
        'body': [
            Q('El Columpio de Huillinco o de los enamorados, fue construido por un matrimonio para celebrar su aniversario 💕.', '[IG-134]'),
            Q('El pueblo de Nercón, que en huilliche significa “entre lomas”, fue una misión indígena fundada por los jesuitas durante la Colonia, que más tarde pasó a estar bajo la dirección de los Franciscanos de Ocopa.', '[IG-110]'),
            Q('Vilupulli, que en mapudungun significa la colina de la serpiente, ha mantenido históricamente un carácter de aldea costera que se agrupa en torno a la Iglesia.', '[IG-130]'),
        ],
        'reviews': [],
    },
    {
        'slug': 'muelle-de-las-almas', 'afiche': '[DEST-H7_004]',
        'title': ('TOUR MUELLE', 'de las', 'ALMAS'),
        'short': 'Tour Muelle de las Almas',
        'hero': 'almas', 'card': 'almas-pareja',
        'gallery': ['almas-2', 'almas-camino', 'almas-grupo', 'almas-pareja', 'huillinco-pareja'],
        'dest': ['cucao-parque'], 'exp': ['mitos', 'naturaleza'],
        'tag': U('Mitos y acantilados', 'Myths and cliffs'),
        'stops': ['Caminata Cordillera Piruil', 'Muelle de las Almas', 'Restaurant tradicional', 'Muelle Lago Huillinco', 'Columpio de los Enamorados'],
        'stop_imgs': ['almas-camino', 'almas', None, None, 'huillinco-pareja'],
        'hook': Q('Este muelle tan mágico nunca pasa de moda😇🌟', '[IG-054]'),
        'lead': Q('El maravilloso Muelle de las Almas, ubicado en la localidad de Cucao es uno de los atractivos turísticos más importantes del Archipiélago de Chiloé!', '[IG-062]'),
        'body': [
            Q('Este representa el inicio del camino que deben seguir las almas después de la muerte, para poder avanzar al más allá🤧', '[IG-062]'),
            Q('En este lugar mágico, donde las almas deben cruzar para ir al más allá, se pueden escuchar los lamentos y súplicas de aquellos que esperan al balsero para que las lleve al descanso eterno💀', '[IG-056]'),
            Q('Con viento y lluvia, se vive la magia y aventura de Chiloé.', '[IG-137]'),
        ],
        'reviews': [],
    },
    {
        'slug': 'muelle-de-la-luz', 'afiche': '[DEST-H7_005]',
        'title': ('TOUR MUELLE', 'de la', 'LUZ'),
        'short': 'Tour Muelle de la Luz',
        'hero': 'muelle-luz-oceano', 'card': 'muelle-luz-mirador',
        'gallery': ['muelle-luz-grupo', 'muelle-luz-sendero', 'pincoya', 'ancud-atardecer', 'punihuil-playa'],
        'dest': ['ancud-punihuil'], 'exp': ['navegacion', 'naturaleza', 'mitos'],
        'tag': U('Frente al Pacífico', 'Facing the Pacific'),
        'stops': ['Navegación Río Chepu', 'Muelle Mirador de la Luz', 'Almuerzo restaurant panorámico', 'Caleta Puñihuil', 'Plaza de Armas Ancud', 'Costanera Ancud'],
        'stop_imgs': [None, 'muelle-luz-mirador', None, 'punihuil-playa', None, 'ancud-atardecer'],
        'hook': Q('✨🌊😌…¿y qué sientes tú, frente a la inmensidad del océano?', '[IG-093]'),
        'lead': Q('El Muelle de la Luz es uno de los más destacados dentro de nuestro hermoso archipiélago y también uno de los más visitados por su acceso directo al océano pacífico🌊', '[IG-022]'),
        'body': [
            Q('La magia de la Pincoya nos acompaña en nuestro viaje al Muelle de la Luz🌅', '[IG-049]'),
            Q('Sí, esto también es parte de nuestro maravilloso Tour Muelle de la Luz.', '[IG-140]'),
            Q('Vive la belleza de Chepu, y de Ancud, junto a @turismochiloemagico 🏞', '[IG-140]'),
        ],
        'reviews': [],
    },
    {
        'slug': 'pinguineras-punihuil', 'afiche': '[DEST-H7_006]',
        'title': ('TOUR PINGÜINERAS', 'de', 'PUÑIHUIL ANCUD'),
        'short': 'Tour Pingüineras de Puñihuil',
        'hero': 'punihuil-bahia', 'card': 'caleuche',
        'gallery': ['punihuil-navega', 'punihuil-bote', 'punihuil-islote', 'punihuil-costa', 'caleuche-2', 'punihuil-playa'],
        'dest': ['ancud-punihuil'], 'exp': ['navegacion', 'naturaleza'],
        'tag': U('Temporada de pingüinos', 'Penguin season'),
        'stops': ['Navegación por 3 islotes', 'Restaurant panorámico', 'Muelle El Caleuche', 'Fuerte San Antonio', 'Feria Artesanal Ancud'],
        'stop_imgs': ['punihuil-navega', None, 'caleuche', None, None],
        'hook': Q('Vamos a navegar? 🌊', '[IG-015]'),
        'lead': Q('Una navegación para poder observar los pingüinos de la corriente Magallánica y Humboldt conviviendo en su habitat veraniego, los islotes de Puñihuil🏝️', '[IG-057]'),
        'body': [
            Q('Al navegar por el Monumento Natural Islotes de Puñihuil, conocemos uno de los pocos lugares del mundo que alberga a colonias de nidificación y reproducción de los pingüinos de Magallanes y de Humboldt.', '[IG-089]'),
            Q('Recuerdos que nos ha dejado este día visitando el Muelle del Caleuche en Puñihuil, donde el amor fue el protagonista ♥️', '[IG-014]'),
        ],
        'season': Q('su habitat veraniego', '[IG-057]'),
        'reviews': ['Jennifer'],
    },
    {
        'slug': 'isla-quinchao', 'afiche': '[DEST-H7_007]',
        'title': ('TOUR', 'Isla', 'QUINCHAO'),
        'short': 'Tour Isla Quinchao',
        'hero': 'curaco', 'card': 'curaco-2',
        'gallery': ['dalcahue', 'dalcahue-feria', 'curaco', 'curaco-2'],
        'dest': ['dalcahue-quinchao'], 'exp': ['patrimonio', 'naturaleza'],
        'tag': U('Iglesias y humedales', 'Churches and wetlands'),
        'stops': ['Feria Artesanal Dalcahue', 'Iglesia Patrimonio Rilán', 'Muelle Mirador Chonos', 'Mirador Changuitad', 'Iglesia Patrimonio Villa Quinchao', 'Costanera Curaco de Vélez', 'Almuerzo en agroturismo', 'Costanera Achao'],
        'stop_imgs': ['dalcahue-feria', None, None, None, None, 'curaco', None, None],
        'hook': Q('Paseo borde Costero #curacodevélez 🐦', '[IG-080]'),
        'lead': Q('Sus extensos y ricos humedales albergan una veintena de aves locales y migratorias que incluyen los zarapitos, que viajan desde Alaska a Chiloé 🌎', '[IG-080]'),
        'body': [Q('La Feria Artesanal de Dalcahue se caracteriza por su arquitectura y sobre todo por su productos y artesanías 💯 locales.', '[IG-075]')],
        'reviews': [],
    },
    {
        'slug': 'isla-mechuque', 'afiche': '[PIEZA IG-017]',
        'title': ('NAVEGACIÓN', 'a', 'ISLA MECHUQUE'),
        'short': 'Isla Mechuque',
        'hero': 'mechuque', 'card': 'mechuque',
        'gallery': [],
        'dest': ['dalcahue-quinchao'], 'exp': ['navegacion', 'gastronomia'],
        'tag': U('Navegación y curanto', 'Boat trip and curanto'),
        'stops': [], 'stop_imgs': [],
        'hook': Q('No te pierdas esta fantástica navegación a la Isla Mechuque para disfrutar de un delicioso curanto en hoyo junto a Chiloé Mágico!', '[IG-025]'),
        'lead': None, 'body': [], 'reviews': [],
        'thin': True,
    },
]

# ---------------------------------------------------------------- DESTINOS
DESTINOS = [
    {'slug': 'castro', 'name': 'Castro', 'img': 'palafitos', 'imgs': ['nercon-2', 'palafitos'],
     'intro': Q('Los Palafitos de Castro⛅️ Uno de los lugares mágicos que nos ofrece Chiloé.', '[IG-024]', fix='se unen dos líneas del original en una'),
     'body': [SITE['salida'], Q('La iglesia Nuestra Señora de Gracia de Nercón es una de las 16 Iglesias Patrimonio de la Humanidad y Monumento Nacional de Chiloé!', '[IG-045]')],
     'must': ['Palafitos de Castro', 'Iglesia de Nercón', 'Plaza de Armas']},
    {'slug': 'ancud-punihuil', 'name': 'Ancud y Puñihuil', 'img': 'punihuil-bahia', 'imgs': ['caleuche', 'muelle-luz-oceano'],
     'intro': Q('Aquí algunos recuerdos de nuestro amigos disfrutando de toda magia y belleza natural que nos ofrece la comuna de Ancud!', '[IG-015]'),
     'body': [Q('La experiencia de ver los pingüinos que ofrece la caleta Puñihuil es de otro nivel🐧', '[IG-057]'), Q('Bello atardecer en la Costanera de Ancud.', '[IG-141]')],
     'must': ['Pingüineras de Puñihuil', 'Muelle El Caleuche', 'Muelle de la Luz', 'Río Chepu', 'Fuerte San Antonio']},
    {'slug': 'dalcahue-quinchao', 'name': 'Dalcahue y Quinchao', 'img': 'tenaun-aereo', 'imgs': ['dalcahue', 'aucar-isla'],
     'intro': Q('En el mapudungun de Chiloé Dalkawe significa lugar de dalcas, es decir, de la embarcación de tres tablones que usaban originalmente los chonos y cuyo uso se difundió a todas las culturas del archipiélago, incuyendo la española.', '[IG-087]', fix='"incuyendo" se deja como en el original'),
     'body': [Q('La iglesia Nuestra Señora del Patrocinio de Tenaún, es una de las 16 Iglesias Patrimonio de la Humanidad y Monumento Nacional en Chiloé😱', '[IG-061]'), Q('Aucar, o Isla de las Almas Navegantes, es un islote conocido por poseer una capilla católica, un cementerio, un parque botánico y una pasarela de 437 m de extensión que le permite estar conectado con la Isla Grande de Chiloé', '[IG-114]', fix='se unen dos líneas del original')],
     'must': ['Feria Artesanal Dalcahue', 'Tenaún', 'Isla Aucar', 'Cascadas de Tocoihue', 'Curaco de Vélez', 'Achao']},
    {'slug': 'chonchi-lemuy', 'name': 'Chonchi e Isla Lemuy', 'img': 'brujos-columpio', 'imgs': ['acordeon', 'yayanes-puente'],
     'intro': Q('Ven a conocer las maravillas que ofrece la Isla Lemuy junto a Turismo Chiloé Mágico🤗', '[IG-055]'),
     'body': [Q('Un bosque de selva fría🌳, en donde predominan árboles nativos como arrayanes y quilas; repleto de senderos mágicos que nos llevan a lugares cada vez más maravillosos🤩', '[IG-067]'), Q('Este encantador hombre tiene una colección de aproximadamente 70 acordeones, los cuales pone a completa disposición de los visitantes que recibe cada día!', '[IG-063]')],
     'must': ['Muelle de los Brujos', 'Parque Yayanes', 'Museo del Acordeón', 'Iglesia de Ichuac', 'Iglesia de Aldachildo', 'Playa Detif']},
    {'slug': 'cucao-parque', 'name': 'Cucao y Parque Nacional', 'img': 'almas-camino', 'imgs': ['parque-bosque', 'almas'],
     'intro': Q('¡Camina junto a nosotros a través de esta generosa reserva nacional de flora y fauna nativa! 🌿', '[IG-071]'),
     'body': [Q('El maravilloso Muelle de las Almas, ubicado en la localidad de Cucao es uno de los atractivos turísticos más importantes del Archipiélago de Chiloé!', '[IG-062]'), Q('Un precioso registro que nos comparte nuestro guía Rodolfo para ilustrar la belleza del Lago Huillinco en nuestro tour al #ParqueNacionalChiloe 🏞️🌳', '[IG-069]')],
     'must': ['Muelle de las Almas', 'Parque Nacional Chiloé', 'Lago Huillinco', 'Humedal Lago Cucao']},
]

EXPERIENCIAS = [
    {'slug': 'patrimonio', 'name': U('Patrimonio e iglesias', 'Heritage and churches'), 'img': 'tenaun',
     'quote': Q('La iglesia San Antonio de Colo, es una de las 16 iglesias patrimonio de la humanidad y monumento nacional de chiloé!', '[IG-038]'),
     'more': Q('La Iglesia de Aldachildo, también conocida como Iglesia de Jesús Nazareno, es un templo católico situado en la localidad de Aldachildo, en la Isla Lemuy. Forma parte del grupo de 16 iglesias de madera de Chiloé calificadas como Monumento Nacional de Chile y reconocidas como Patrimonio de la Humanidad por la Unesco.', '[IG-146]', fix='se unen dos líneas del original')},
    {'slug': 'naturaleza', 'name': U('Naturaleza y fauna', 'Nature and wildlife'), 'img': 'yayanes-puente',
     'quote': Q('Caminar entre bosque y mar es lo mágico de Chiloé 🌳🌊🤗', '[IG-083]'),
     'more': Q('Un bosque de selva fría🌳, en donde predominan árboles nativos como arrayanes y quilas; repleto de senderos mágicos que nos llevan a lugares cada vez más maravillosos🤩', '[IG-067]')},
    {'slug': 'navegacion', 'name': U('Navegación', 'Boat trips'), 'img': 'punihuil-navega',
     'quote': Q('Vamos a navegar? 🌊', '[IG-015]'),
     'more': Q('Una navegación para poder observar los pingüinos de la corriente Magallánica y Humboldt conviviendo en su habitat veraniego, los islotes de Puñihuil🏝️', '[IG-057]')},
    {'slug': 'gastronomia', 'name': U('Gastronomía chilota', 'Chilote food'), 'img': 'curanto-destape',
     'quote': Q('¡Llegó la hora del destape! #curantoalhoyo 🔥🥔🥓', '[IG-086]'),
     'more': Q('Se compone fundamentalmente de mariscos, papas, junto a  otras preparaciones tradicionales de esta zona como el milcao y el chapalele, a la que se le añade carne, pollo y embutidos...', '[IG-034]')},
    {'slug': 'mitos', 'name': U('Mitos y leyendas', 'Myths and legends'), 'img': 'brujos-vuelo',
     'quote': Q('Tal como lo hacen los brujos y brujas de Chiloé, nuestros turistas aprovecharon la visita al  @muelledelosbrujoschiloe en Yelqui para practicar el vuelo 🧙‍♀️🧹🧙‍♂️', '[IG-070]'),
     'more': Q('El lugar es magnífico y no sólo por lo denso del bosque y lo espectacular del salto de agua. El sitio está lleno de misterio y mitología, pues el mito indica que esta cascada es la usada por los brujos de Chiloé para borrarse el bautismo cristiano.', '[IG-123]')},
]

PAQUETES = [
    {'slug': 'valdivia-niebla', 'name': 'Valdivia y Niebla', 'days': U('4 días · 3 noches', '4 days · 3 nights'), 'imgs': ['valdivia', 'valdivia-2'],
     'text': Q('Otra salida marcada por innumerable recuerdos, una agradecimiento a nuestros amigos por contar con nosotros, excursión Valdivia y Niebla 4 días - 3 noches 🤗', '[IG-016]')},
    {'slug': 'nieve-volcan-osorno', 'name': 'Circuito a la nieve: Volcán Osorno', 'days': U('Circuito publicado en 2023', 'Circuit published in 2023'), 'imgs': ['osorno'],
     'text': Q('recorrido de castro al volcán Osorno🏔, visitando  salto de petrohue y el lago todos los santos, no te pierdas de esta increíble experiencia para vivirla junto a tus familiares y amigos', '[IG-031]'),
     },
    {'slug': 'bariloche', 'name': 'San Carlos de Bariloche', 'days': U('Viaje internacional', 'International trip'), 'imgs': ['nieve', 'nieve-2'],
     'text': Q('La nieve, paisajes hermosos y todo lo que San Carlos de Bariloche puede ofrecer....... los esperamos para repetir esta experiencia', '[IG-030]')},
]

GUIA = [
    {'slug': 'que-es-el-curanto', 'title': U('¿Qué es el curanto?', 'What is curanto?'), 'img': 'curanto-fuego', 'src': '[IG-034]',
     'paras': [Q('Te estarás preguntando ¿que es el curanto?', '[IG-034]'),
               Q('El curanto en hoyo o curanto al hoyo, es una milenaria técnica de cocción que utiliza piedras calientes en un hoyo excavado en la tierra para cocinar los alimentos, los cuales se tapan con hojas de pague, permitiendo una cocción al vapor con toques ahumados', '[IG-034]'),
               Q('Se compone fundamentalmente de mariscos, papas, junto a  otras preparaciones tradicionales de esta zona como el milcao y el chapalele, a la que se le añade carne, pollo y embutidos...', '[IG-034]'),
               Q('Que no te lo cuenten y ven a comerte un rico curanto con nosotros', '[IG-034]')], 'tours': ['la-costa-curanto', 'isla-mechuque']},
    {'slug': 'iglesias-patrimonio', 'title': U('Las iglesias patrimonio', 'The heritage churches'), 'img': 'nercon', 'src': '[IG-096][IG-045][IG-146]',
     'paras': [Q('La iglesia está asentada en una base de piedras y madera de coigüe. Su estructura está compuesta principalmente por madera de tepa, tenío y canelo. El revestimiento interior es de madera de alerce, mientras que el revestimiento exterior es de tejuelas de alerce y traslapo de ciprés de las Guaitecas y alerce.', '[IG-096]'),
               Q('Es una de las más importantes por su reconocido color y forma con 3 torres', '[IG-061]'),
               Q('Vilupulli se caracteriza por su condición de aldea costera que surge en torno a la iglesia, en la que se conservan los espacios ceremoniales característicos de la misión circular, así como su entorno paisajístico de alta importancia, dadas sus condiciones geográficas.', '[IG-112]'),
               Q('Maravilloso día nos tocó en nuestra visita a la Isla de Lemuy☀️. En esta oportunidad podemos ver la Iglesia de Ichuac, Natividad de María, que es una de las 16 Iglesias Patrimoniales de Chiloé⛪️', '[IG-068]')], 'tours': ['la-costa-curanto', 'parque-nacional-chiloe', 'isla-lemuy-asado', 'isla-quinchao']},
    {'slug': 'brujos-almas-y-pincoya', 'title': U('Brujos, almas y la Pincoya', 'Witches, souls and the Pincoya'), 'img': 'brujos-alas', 'src': '[IG-131][IG-056][IG-049]',
     'paras': [Q('¿Sabías que en las #cascadasdetocoihue se iniciaban los brujos?', '[IG-131]'),
               Q('En este lugar mágico, donde las almas deben cruzar para ir al más allá, se pueden escuchar los lamentos y súplicas de aquellos que esperan al balsero para que las lleve al descanso eterno💀', '[IG-056]'),
               Q('La magia de la Pincoya nos acompaña en nuestro viaje al Muelle de la Luz🌅', '[IG-049]'),
               Q('¿Ángel o diablo? 😇 😈 … con @turismochiloemagico todo puede pasar 😉', '[IG-094]')], 'tours': ['muelle-de-las-almas', 'isla-lemuy-asado', 'la-costa-curanto']},
    {'slug': 'la-minga', 'title': U('La minga', 'The minga'), 'img': 'minga', 'src': '[IG-066]',
     'paras': [Q('Una de las actividades más especiales que puede ofrecer el Archipiélago de Chiloé es la Minga🤠', '[IG-066]'),
               Q('Una minga es una tradición antigua enfocada en el trabajo agrícola colectivo a beneficio de un vecino o comunidad general. En este caso la "tiradura de casa" es la expresión más popular de dicha tradición🏠', '[IG-066]'),
               Q('En esta ocasión, Turismo Chiloé Mágico hizo posible que muchas personas sean testigos de esta increíble hazaña cultural chilota🤩', '[IG-066]')], 'tours': []},
    {'slug': 'pinguinos-de-punihuil', 'title': U('Los pingüinos de Puñihuil', 'The penguins of Puñihuil'), 'img': 'punihuil-islote', 'src': '[IG-089][IG-057]',
     'paras': [Q('Al navegar por el Monumento Natural Islotes de Puñihuil, conocemos uno de los pocos lugares del mundo que alberga a colonias de nidificación y reproducción de los pingüinos de Magallanes y de Humboldt.', '[IG-089]'),
               Q('El magnífico hogar de los pingüinos en su estadía por nuestro archipiélago🐧', '[IG-053]'),
               Q('…el sector de Puñihuil, que se destaca por la protección de pingüinos de Magallanes y de Humboldt 🐧', '[IG-122]', fix='Se omite "Este Domingo 02, puedes conocer" (fecha vencida)')], 'tours': ['pinguineras-punihuil', 'muelle-de-la-luz']},
]

# Reseñas: nombre de pila, idioma, tour y cita literal (con "…" si se corta). Fuente: Google Maps, 19-oct-2026.
REVIEWS = [
    {'name': 'Javiera', 'lang': 'es', 'tour': 'isla-lemuy-asado', 'text': Q('…Respecto a los lugares que conocimos, todos tenían un sentido, todos los lugares maravillosos. Nuestros favoritos, la casa de don Hugo con el asado de cordero y el perrito Simón, la Isla Aucar, Chonchi y su museo del acordeón, pero muy especialmente ese exquisito Curanto al Hoyo inolvidable del segundo día. …', '[RESEÑA Javiera Blanco, Google]')},
    {'name': 'Zarana', 'lang': 'en', 'text': Q('Sandra was a great tour guide and really showed us the charm of chiloe. The agency has great communication and were very accommodating with our last minute reservation. Everything ran smoothly. They were able to add vegetarian meals at the restaurant.', '[RESEÑA Zarana Bayona, Google]')},
    {'name': 'Andrea', 'lang': 'es', 'tour': 'isla-lemuy-asado', 'text': Q('Tuvimos un día completo de tour a la isla de Lemuy. Super puntuales, muy  agradable el trato en todo momento. Alberto, el guía lo da todo, explica y atiende cada pregunta, está atento a todo. Transmite el amor por la tierra y la cultura chilota. …', '[RESEÑA Andrea Della Penna, Google]')},
    {'name': 'elia', 'lang': 'en', 'text': Q('I enjoyed the myths of brujería and the taste of chiloe with Nicolas. A sympathetic guide tour who made us laugh a lot with a million stories. …', '[RESEÑA elia loddo, Google]')},
    {'name': 'Ximena', 'lang': 'es', 'tour': 'la-costa-curanto', 'text': Q('…Fuimos con mi familia al tour de la costa, pues queríamos conocer la Isla Aucar y comer curanto en hoyo. Además de eso, pudimos conocer Dalcahue, Tenaún y la cascada de Tocoihue. El tour fue preciso, teníamos tiempo para recorrer libremente y solo acordábamos la hora de reunión para ir a otro lugar, vimos el proceso del curanto y aprendimos muchísimo de cada localidad. …', '[RESEÑA Ximena González Vargas, Google]')},
    {'name': 'Luciano', 'lang': 'en', 'text': Q('Great tours. Welcoming and attentive staff. Check the tour schedule and have fun.', '[RESEÑA Luciano Deluqui Vasques, Google]')},
    {'name': 'Valeria', 'lang': 'es', 'tour': 'la-costa-curanto', 'text': Q('Fuimos junto a mi pareja a realizar el tour de la costa . Nuestro Guía Nicolás muy amable, informado y divertido. Don Enrique nuestro conductor muy preocupado y gentil. Fue una excelente experiencia en invierno , 100% recomendable. …', '[RESEÑA Valeria Carvajal, Google]')},
    {'name': 'Jennifer', 'from': 'Iquique', 'lang': 'es', 'tour': 'pinguineras-punihuil', 'text': Q('Quedamos muy contentos con el tour a las pingüinera y con el de la costa con curanto muy recomendado y el guía Alberto excelente persona y profesional y mencionar a don Enrique que nos transportó a todos esos lugares hermosos en forma segura muchas gracias desde Iquique .', '[RESEÑA Jennifer muñoz, Google]')},
    {'name': 'Gabriela', 'lang': 'es', 'text': Q('Tomé tres tours con ellos y lo recomiendo. El transporte es en vehículos pequeños pero cómodos, lo cual hace que la experiencia sea muy personalizada. …', '[RESEÑA Gabriela Vallejos Carrasco, Google]')},
    {'name': 'Alexandra', 'lang': 'es', 'text': Q('Agradecemos a chiloe mágico por tan linda experiencia tomamos todos los tour con ellos 4 días seguidos!! … 10/10 el servicio sin duda lo recomendamos y volveríamos a elegirlos! …', '[RESEÑA Alexandra Ilabaca, Google]')},
    {'name': 'Jaime', 'lang': 'es', 'tour': 'la-costa-curanto', 'text': Q('Una excelente experiencia la del Tour La Costa!!! Desde el guía Alberto, conductor Enrique, transporte, comida y lugares por visitar son hermosos. …', '[RESEÑA Jaime Galaz, Google]')},
    {'name': 'Francesca', 'lang': 'es', 'tour': 'isla-lemuy-asado', 'text': Q('Tomamos con mi amiga el tour Isla Lemuy, excelente el guía, la comida y los lugares. …', '[RESEÑA Francesca Cruzat, Google]')},
    {'name': 'susan', 'lang': 'es', 'tour': 'isla-lemuy-asado', 'text': Q('…la comida que incluye el tour a isla Lemuy es demasiado rico y puedes comer hasta quedar satisfecho. Recorrimos lugares hermosos y convivimos con locales eso hace mucho mejor la experiencia. …', '[RESEÑA susan mtv, Google]')},
]

TEAM = [
    {'name': 'Nicolás', 'role': U('Guía', 'Guide'), 'src': '[IG-023][IG-070][RESEÑA]'},
    {'name': 'Alberto', 'role': U('Guía', 'Guide'), 'src': '[RESEÑA]'},
    {'name': 'Meli', 'role': U('Guía', 'Guide'), 'src': '[IG-004][RESEÑA]'},
    {'name': 'Sandra', 'role': U('Guía', 'Guide'), 'src': '[RESEÑA]'},
    {'name': 'Rodolfo', 'role': U('Guía', 'Guide'), 'src': '[IG-069]'},
    {'name': 'Don Enrique', 'role': U('Conductor', 'Driver'), 'src': '[IG-060][RESEÑA]'},
    {'name': 'Marcelo', 'role': U('Conductor', 'Driver'), 'src': '[RESEÑA]'},
    {'name': 'Marco', 'role': U('Conductor', 'Driver'), 'src': '[RESEÑA]'},
]

FAQ = [
    (U('¿Desde dónde salen los tours?', 'Where do tours depart from?'), [SITE['salida'], SITE['address_short']]),
    (U('¿A qué hora salen y vuelven?', 'What time do they leave and return?'), [SITE['horario_tour']]),
    (U('¿Qué incluye cada tour?', 'What does each tour include?'), [Q('Todos nuestros tours incluyen traslado, guiado, almuerzo y bebestibles, y visitas a distintos atractivos turísticos 🌿', '[IG-007]')]),
    (U('¿Cuántas personas van por grupo?', 'How many people per group?'), [SITE['van16']]),
    (U('¿Hay tours todos los días?', 'Are there tours every day?'), [SITE['bio1'], SITE['cupos']]),
    (U('¿En qué idioma es el guiado?', 'What language is the guiding in?'), ['__es_only__', SITE['idioma']]),
    (U('¿Qué pasa si llueve?', 'What if it rains?'), [SITE['clima'], '__pending__']),
    (U('¿Hay opción vegetariana?', 'Is there a vegetarian option?'), [Q('They were able to add vegetarian meals at the restaurant.', '[RESEÑA Zarana Bayona, Google]'), '__pending__']),
    (U('¿Cuánto cuesta?', 'How much does it cost?'), ['__costa__', Q('💵Valor: $35.000 por persona (incluyendo el almuerzo) + $3.000 por persona (entrada a las cascadas)', '[IG-006]'), '__pending_prices__']),
    (U('¿Cómo reservo?', 'How do I book?'), ['__wa__', SITE['cupos']]),
    (U('¿Cuál es la política de cancelación?', 'What is the cancellation policy?'), ['__pending__']),
    (U('¿Cómo se paga?', 'How do I pay?'), ['__pending__']),
    (U('¿Pueden ir niños?', 'Can children come?'), ['__pending__']),
    (U('¿Cuál es el horario de la agencia?', 'What are the office hours?'), [SITE['hours']]),
]


# ---------------------------------------------------------------- v5: ficha de cada tour
# Texto de interfaz escrito a partir de datos verificables (afiche del tour y sus publicaciones);
# las citas literales de la marca siguen en TOURS (hook, lead, body). Fuente de cada dato al lado.
DETAIL = {
    'la-costa-curanto': {
        'corto': U('Curanto en hoyo, iglesia de Tenaún, cascadas e Isla Aucar.', 'Pit curanto, Tenaún church, waterfalls and Aucar Island.'),
        'que': U('Curanto en hoyo frente a las Islas Chauques, la iglesia de Tenaún, las cascadas de Tocoihue y la pasarela a Isla Aucar.',
                 'Pit-cooked curanto facing the Chauques Islands, Tenaún church, Tocoihue falls and the footbridge to Aucar Island.'),  # [DEST-H7_002] + IG
        'lunch': U('Curanto en hoyo', 'Pit-cooked curanto'),
        'pts': [U('Ves preparar y destapar el curanto en hoyo, con mirador a las Islas Chauques', 'Watch the curanto being cooked and uncovered in the pit, overlooking the Chauques Islands'),
                U('Iglesia Patrimonio de la Humanidad de Tenaún', 'Tenaún church, a UNESCO World Heritage Site'),
                U('Cascadas de Tocoihue, donde según la leyenda se iniciaban los brujos', 'Tocoihue falls, where legend says the witches were initiated'),
                U('Pasarela de 437 metros sobre el mar hasta la Isla Aucar', 'A 437-metre footbridge over the sea to Aucar Island'),
                U('Feria Artesanal de Dalcahue', 'Dalcahue craft market')],
        'no': [U('$3.000 por persona: entrada a las cascadas', 'CLP 3,000 per person: falls entrance')],  # [DEST-H7_002]
        'rel': ['isla-mechuque', 'isla-quinchao', 'isla-lemuy-asado'],
    },
    'isla-lemuy-asado': {
        'corto': U('Navegación a Lemuy, Muelle de los Brujos y asado al palo.', "Boat to Lemuy, the Witches' Pier and spit-roast lamb."),
        'que': U('Navegas el canal Yal hasta Isla Lemuy, vuelas en escoba en el Muelle de los Brujos y almuerzas asado de cordero al palo.',
                 'Cross the Yal channel to Lemuy Island, fly on a broom at the Witches\' Pier and have spit-roast lamb for lunch.'),  # [DEST-H7_008] + IG
        'lunch': U('Asado de cordero al palo', 'Spit-roast lamb'),
        'pts': [U('Navegación por el canal Yal hasta Isla Lemuy', 'Crossing the Yal channel to Lemuy Island'),
                U('Fotos "volando" en el Muelle de los Brujos', '"Flying" photos at the Witches\' Pier'),
                U('Puente colgante de 30 metros en el Parque Yayanes', '30-metre suspension bridge in Yayanes Park'),
                U('Iglesia Patrimonio de Vilupulli y el Museo del Acordeón en Chonchi', 'Vilupulli heritage church and the Accordion Museum in Chonchi'),
                U('Almuerzo de asado de cordero al palo en agroturismo', 'Spit-roast lamb lunch at a farm')],
        'no': [], 'rel': ['la-costa-curanto', 'parque-nacional-chiloe', 'muelle-de-las-almas'],
    },
    'parque-nacional-chiloe': {
        'corto': U('Bosque nativo y playa en el Parque Nacional, más Nercón y Huillinco.', 'Native forest and beach in the National Park, plus Nercón and Huillinco.'),
        'que': U('Caminas por el bosque nativo del Parque Nacional Chiloé hasta la playa, con paradas en Nercón, Chonchi y el columpio de Huillinco.',
                 'Walk through the native forest of Chiloé National Park to the beach, stopping at Nercón, Chonchi and the Huillinco swing.'),  # [DEST-H7_003]
        'lunch': U('Almuerzo en restaurant tradicional', 'Lunch at a traditional restaurant'),
        'pts': [U('Senderos del Parque Nacional Chiloé y la playa Chanquín', 'Chiloé National Park trails and Chanquín beach'),
                U('Iglesia Patrimonio de Nercón', 'Nercón heritage church'),
                U('Columpio de los Enamorados en el lago Huillinco', 'The Lovers\' Swing on Lake Huillinco'),
                U('Artesanía en Chonchi', 'Crafts in Chonchi')],
        'no': [], 'rel': ['muelle-de-las-almas', 'isla-lemuy-asado', 'muelle-de-la-luz'],
    },
    'muelle-de-las-almas': {
        'corto': U('Caminata a los acantilados de Cucao y el Muelle de las Almas.', 'A walk to the Cucao cliffs and the Pier of Souls.'),
        'que': U('Caminata por la cordillera de Piruil hasta el Muelle de las Almas, sobre los acantilados de Cucao, y el lago Huillinco.',
                 'A walk over the Piruil range to the Pier of Souls above the Cucao cliffs, then Lake Huillinco.'),  # [DEST-H7_004]
        'lunch': U('Almuerzo en restaurant tradicional', 'Lunch at a traditional restaurant'),
        'pts': [U('Caminata por la cordillera de Piruil', 'Walk over the Piruil range'),
                U('Muelle de las Almas, frente al Pacífico', 'The Pier of Souls, facing the Pacific'),
                U('La leyenda del balsero que lleva las almas al más allá', 'The legend of the ferryman who carries souls to the afterlife'),
                U('Muelle y Columpio de los Enamorados en el lago Huillinco', 'Pier and Lovers\' Swing on Lake Huillinco')],
        'no': [], 'rel': ['parque-nacional-chiloe', 'muelle-de-la-luz', 'isla-lemuy-asado'],
    },
    'muelle-de-la-luz': {
        'corto': U('Navegación por el río Chepu y el muelle frente al Pacífico.', 'A Chepu river boat ride and the pier facing the Pacific.'),
        'que': U('Navegas el río Chepu, caminas al Muelle de la Luz frente al océano y terminas en Puñihuil y Ancud.',
                 'Sail the Chepu river, walk to the Muelle de la Luz facing the ocean and finish at Puñihuil and Ancud.'),  # [DEST-H7_005]
        'lunch': U('Almuerzo en restaurant panorámico', 'Lunch at a panoramic restaurant'),
        'pts': [U('Navegación por el río Chepu', 'Sailing the Chepu river'),
                U('Muelle Mirador de la Luz, sobre el Pacífico', 'Muelle de la Luz lookout over the Pacific'),
                U('Caleta Puñihuil y la escultura de la Pincoya', 'Puñihuil cove and the Pincoya sculpture'),
                U('Plaza de Armas y costanera de Ancud', 'Ancud main square and waterfront')],
        'no': [], 'rel': ['pinguineras-punihuil', 'muelle-de-las-almas', 'parque-nacional-chiloe'],
    },
    'pinguineras-punihuil': {
        'corto': U('Navegación a ver pingüinos en los islotes de Puñihuil.', 'A boat trip to see penguins at the Puñihuil islets.'),
        'que': U('Navegas entre los islotes de Puñihuil para ver pingüinos de Magallanes y de Humboldt, y sigues al Muelle El Caleuche y Ancud.',
                 'Sail among the Puñihuil islets to see Magellanic and Humboldt penguins, then the Caleuche pier and Ancud.'),  # [DEST-H7_006] + IG
        'lunch': U('Almuerzo en restaurant panorámico', 'Lunch at a panoramic restaurant'),
        'pts': [U('Navegación por 3 islotes del Monumento Natural Puñihuil', 'Boat trip around 3 islets of the Puñihuil Natural Monument'),
                U('Pingüinos de Magallanes y de Humboldt en su temporada de verano', 'Magellanic and Humboldt penguins in their summer season'),
                U('Muelle El Caleuche', 'El Caleuche pier'),
                U('Fuerte San Antonio y Feria Artesanal de Ancud', 'San Antonio fort and Ancud craft market')],
        'no': [], 'season': U('Pingüinos en verano. Meses exactos: por confirmar con la agencia.', 'Penguins in summer. Exact months: to be confirmed with the agency.'),
        'rel': ['muelle-de-la-luz', 'isla-mechuque', 'la-costa-curanto'],
    },
    'isla-quinchao': {
        'corto': U('Feria de Dalcahue, iglesias patrimonio y humedales de Curaco.', 'Dalcahue market, heritage churches and Curaco wetlands.'),
        'que': U('Cruzas a Isla Quinchao: feria de Dalcahue, iglesias patrimonio de Rilán y Villa Quinchao, miradores y los humedales de Curaco de Vélez.',
                 'Cross to Quinchao Island: Dalcahue market, Rilán and Villa Quinchao heritage churches, lookouts and the Curaco de Vélez wetlands.'),  # [DEST-H7_007]
        'lunch': U('Almuerzo incluido', 'Lunch included'),
        'pts': [U('Feria Artesanal de Dalcahue', 'Dalcahue craft market'),
                U('Iglesias Patrimonio de Rilán y Villa Quinchao', 'Rilán and Villa Quinchao heritage churches'),
                U('Miradores Chonos y Changuitad', 'Chonos and Changuitad lookouts'),
                U('Costanera y humedales de Curaco de Vélez, con aves migratorias', 'Curaco de Vélez waterfront and wetlands, with migratory birds')],
        'no': [], 'rel': ['la-costa-curanto', 'isla-mechuque', 'isla-lemuy-asado'],
    },
    'isla-mechuque': {
        'corto': U('Navegación a la Isla Mechuque con curanto en hoyo.', 'A boat trip to Mechuque Island with pit curanto.'),
        'que': U('Navegas a la Isla Mechuque y almuerzas curanto en hoyo.', 'Sail to Mechuque Island and have pit-cooked curanto for lunch.'),  # [PIEZA IG-017]
        'lunch': U('Curanto en hoyo', 'Pit-cooked curanto'),
        'pts': [U('Navegación a la Isla Mechuque', 'Boat trip to Mechuque Island'),
                U('Curanto en hoyo', 'Pit-cooked curanto')],
        'no': [], 'rel': ['la-costa-curanto', 'isla-quinchao', 'pinguineras-punihuil'],
    },
}
