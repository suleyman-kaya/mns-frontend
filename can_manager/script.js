$(document).ready(function () {
    var canvas = document.getElementById('myCanvas');
    var ctx = canvas.getContext('2d');

    canvas.width = window.innerWidth * 0.8;
    canvas.height = window.innerHeight * 0.8;

    var shapes = [];
    var selectedShape = null;
    var dragStartX, dragStartY;
    var draggingShape = false;
    var draggingPin = null;
    var connectingLine = null;

    // Şekil objesi
    function Shape(type, x, y, width, height, inputCount, outputCount) {
        this.type = type;
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.inputCount = inputCount;
        this.outputCount = outputCount;
        this.inputPins = [];
        this.outputPins = [];
        this.connections = [];

        // Pin oluşturma fonksiyonu
        this.createPins = function () {
            var pinHeight = this.height / (this.inputCount + 1);
            for (var i = 1; i <= this.inputCount; i++) {
                this.inputPins.push({ x: this.x, y: this.y + i * pinHeight });
            }
            for (var j = 1; j <= this.outputCount; j++) {
                this.outputPins.push({ x: this.x + this.width, y: this.y + j * pinHeight });
            }
        };

        // Şekli çizme fonksiyonu
        this.draw = function () {
            ctx.beginPath();
            if (this.type === 'rectangle') {
                ctx.rect(this.x, this.y, this.width, this.height);
            } else if (this.type === 'ellipse') {
                ctx.ellipse(this.x + this.width / 2, this.y + this.height / 2, this.width / 2, this.height / 2, 0, 0, 2 * Math.PI);
            } else if (this.type === 'parallelogram') {
                ctx.moveTo(this.x, this.y);
                ctx.lineTo(this.x + this.width * 0.6, this.y);
                ctx.lineTo(this.x + this.width, this.y + this.height);
                ctx.lineTo(this.x + this.width * 0.4, this.y + this.height);
                ctx.closePath();
            }
            ctx.stroke();

            // Pinleri çizme
            ctx.fillStyle = 'black';
            this.inputPins.forEach(function (pin) {
                ctx.beginPath();
                ctx.arc(pin.x, pin.y, 3, 0, 2 * Math.PI);
                ctx.fill();
            });
            this.outputPins.forEach(function (pin) {
                ctx.beginPath();
                ctx.arc(pin.x, pin.y, 3, 0, 2 * Math.PI);
                ctx.fill();
            });
        };

        // Şeklin içinde mi kontrolü
        this.isInside = function (mouseX, mouseY) {
            if (mouseX >= this.x && mouseX <= this.x + this.width && mouseY >= this.y && mouseY <= this.y + this.height) {
                return true;
            }
            return false;
        };

        // Pinin içinde mi kontrolü
        this.pinIsInside = function (pinX, pinY, mouseX, mouseY) {
            var radius = 5; // Pinin tıklanabilir alanı
            if (mouseX >= pinX - radius && mouseX <= pinX + radius && mouseY >= pinY - radius && mouseY <= pinY + radius) {
                return true;
            }
            return false;
        };

        // Şekli ve pinleri sürükleme fonksiyonu
        this.move = function (dx, dy) {
            this.x += dx;
            this.y += dy;

            var pinHeight = this.height / (this.inputCount + 1);
            for (var i = 0; i < this.inputPins.length; i++) {
                this.inputPins[i].x += dx;
                this.inputPins[i].y += dy;
            }
            for (var j = 0; j < this.outputPins.length; j++) {
                this.outputPins[j].x += dx;
                this.outputPins[j].y += dy;
            }
        };
    }

    // Canvas üzerindeki tıklama işlemleri
    canvas.addEventListener('mousedown', function (e) {
        var mouseX = e.clientX - canvas.getBoundingClientRect().left;
        var mouseY = e.clientY - canvas.getBoundingClientRect().top;

        shapes.forEach(function (shape) {
            if (shape.isInside(mouseX, mouseY)) {
                selectedShape = shape;
                draggingShape = true;
                dragStartX = mouseX - shape.x;
                dragStartY = mouseY - shape.y;

                shape.inputPins.forEach(function (pin) {
                    if (shape.pinIsInside(pin.x, pin.y, mouseX, mouseY)) {
                        draggingPin = pin;
                        connectingLine = { startX: pin.x, startY: pin.y, endX: mouseX, endY: mouseY, pin: pin };
                        return;
                    }
                });
                shape.outputPins.forEach(function (pin) {
                    if (shape.pinIsInside(pin.x, pin.y, mouseX, mouseY)) {
                        draggingPin = pin;
                        connectingLine = { startX: pin.x, startY: pin.y, endX: mouseX, endY: mouseY, pin: pin };
                        return;
                    }
                });

                return;
            }
        });
    });

    canvas.addEventListener('mousemove', function (e) {
        if (draggingShape) {
            var mouseX = e.clientX - canvas.getBoundingClientRect().left;
            var mouseY = e.clientY - canvas.getBoundingClientRect().top;

            if (draggingPin) {
                connectingLine.endX = mouseX;
                connectingLine.endY = mouseY;
            } else {
                var dx = mouseX - dragStartX - selectedShape.x;
                var dy = mouseY - dragStartY - selectedShape.y;
                selectedShape.move(dx, dy);
            }
            updateCanvas();
        }
    });

    canvas.addEventListener('mouseup', function (e) {
        draggingShape = false;
        selectedShape = null;

        if (draggingPin) {
            var mouseX = e.clientX - canvas.getBoundingClientRect().left;
            var mouseY = e.clientY - canvas.getBoundingClientRect().top;

            shapes.forEach(function (shape) {
                shape.inputPins.forEach(function (pin) {
                    if (shape.pinIsInside(pin.x, pin.y, mouseX, mouseY) && pin !== draggingPin) {
                        draggingPin.connectedPin = pin;
                        shape.connections.push({ startPin: draggingPin, endPin: pin });
                    }
                });
                shape.outputPins.forEach(function (pin) {
                    if (shape.pinIsInside(pin.x, pin.y, mouseX, mouseY) && pin !== draggingPin) {
                        draggingPin.connectedPin = pin;
                        shape.connections.push({ startPin: draggingPin, endPin: pin });
                    }
                });
            });

            draggingPin = null;
            connectingLine = null;
            updateCanvas();
        }
    });

    $('#btnRect').click(function () {
        var inputCount = parseInt($('#inputCount').val());
        var outputCount = parseInt($('#outputCount').val());
        var rectWidth = 100;
        var rectHeight = 50;
        var rectX = canvas.width / 2 - rectWidth / 2;
        var rectY = canvas.height / 2 - rectHeight / 2;

        var rectangle = new Shape('rectangle', rectX, rectY, rectWidth, rectHeight, inputCount, outputCount);
        rectangle.createPins();
        shapes.push(rectangle);
        updateCanvas();
    });

    $('#btnEllipse').click(function () {
        var inputCount = parseInt($('#inputCount').val());
        var outputCount = parseInt($('#outputCount').val());
        var ellipseWidth = 100;
        var ellipseHeight = 50;
        var ellipseX = canvas.width / 2 - ellipseWidth / 2;
        var ellipseY = canvas.height / 2 - ellipseHeight / 2;

        var ellipse = new Shape('ellipse', ellipseX, ellipseY, ellipseWidth, ellipseHeight, inputCount, outputCount);
        ellipse.createPins();
        shapes.push(ellipse);
        updateCanvas();
    });

    $('#btnParallelogram').click(function () {
        var inputCount = parseInt($('#inputCount').val());
        var outputCount = parseInt($('#outputCount').val());
        var paraWidth = 100;
        var paraHeight = 50;
        var paraX = canvas.width / 2 - paraWidth / 2;
        var paraY = canvas.height / 2 - paraHeight / 2;

        var parallelogram = new Shape('parallelogram', paraX, paraY, paraWidth, paraHeight, inputCount, outputCount);
        parallelogram.createPins();
        shapes.push(parallelogram);
        updateCanvas();
    });

    function updateCanvas() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        shapes.forEach(function (shape) {
            shape.draw();
            shape.connections.forEach(function (connection) {
                ctx.beginPath();
                ctx.moveTo(connection.startPin.x, connection.startPin.y);
                ctx.lineTo(connection.endPin.x, connection.endPin.y);
                ctx.strokeStyle = 'green';
                ctx.stroke();
            });
        });

        if (connectingLine) {
            ctx.beginPath();
            ctx.moveTo(connectingLine.startX, connectingLine.startY);
            ctx.lineTo(connectingLine.endX, connectingLine.endY);
            ctx.strokeStyle = 'red';
            ctx.stroke();
        }
    }
});
