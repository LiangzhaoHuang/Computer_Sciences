# Rectangle Game (Nand2Tetris Project)

This is a simple interactive graphical game written in Jack, the high-level language used in the Nand2Tetris course. The game features a rectangle that the user can move and resize on the screen using keyboard input.

## 📁 Files

- `Main.jack` – Entry point; initializes and runs the rectangle game
- `RectangleGame.jack` – Controls the game loop and handles keyboard interaction
- `Rectangle.jack` – Defines the rectangle object and its behavior (draw, erase, move, resize)

## 🎮 Controls

- `Arrow Keys` – Move the rectangle on screen
- `x` – Decrease width (shrink horizontally)
- `X` – Increase width (expand horizontally)
- `y` – Decrease height (shrink vertically)
- `Y` – Increase height (expand vertically)
- `Q` – Quit the game

> 🧊 The rectangle will not respond to input while no key is pressed (`key = 0`).

## 🚀 How to Run

1. Compile all `.jack` files using the `JackCompiler`
2. Load the resulting `.vm` files into the **VM Emulator**
3. Use the keyboard to move and resize the rectangle

## ✨ Features

- Pixel-level graphics using `Screen.drawLine()` and `setPixel()`
- Real-time input via `Keyboard.keyPressed()`
- Manual memory handling with `Memory.alloc()` / `deAlloc()`
- Responsive movement and scaling with bounds checks

---

Enjoy coding and customizing your rectangle game!

