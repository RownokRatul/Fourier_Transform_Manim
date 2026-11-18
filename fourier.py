from manim import *
import numpy as np


class FourierPortrait(Scene):

  def construct(self):
    svg_mob = SVGMobject("fourier.svg")
    main_path = max(svg_mob.family_members_with_points(), key=lambda m: len(m.points))
    
    N = 400
    alphas = np.linspace(0, 1, N, endpoint=False)
    sampled_points = np.array([main_path.point_from_proportion(a) for a in alphas])
    
    complex_points = sampled_points[:, 0] + 1j * sampled_points[:, 1]
    
    complex_points -= np.mean(complex_points)
    complex_points *= 2.5 / np.max(np.abs(complex_points))

    fft_coeffs = np.fft.fft(complex_points) / N
    freqs = np.fft.fftfreq(N, d=1.0 / N)

    components = []
    for k in range(N):
      coeff = fft_coeffs[k]
      freq = freqs[k]
      radius = np.abs(coeff)
      phase = np.angle(coeff)
      components.append((radius, freq, phase))
    
    components.sort(key=lambda x: x[0], reverse=True)

    M = 150
    components = components[:M]

    t_tracker = ValueTracker(0)

    circles = VGroup()
    vectors = VGroup()

    for radius, freq, phase in components:
      circle = Circle(
          radius=radius,
          stroke_width=1,
          stroke_color=BLUE_E,
          stroke_opacity=0.45,
      )
      vector = Line(
          ORIGIN,
          RIGHT * radius,
          stroke_width=1.5,
          color=WHITE,
          stroke_opacity=0.8,
      )
      circles.add(circle)
      vectors.add(vector)

    def update_epicycles(mob):
      t = t_tracker.get_value()
      current_pos = np.array([0.0, 0.0, 0.0])

      for i, (radius, freq, phase) in enumerate(components):
        angle = 2 * np.pi * freq * t + phase
        next_pos = current_pos + np.array([
            radius * np.cos(angle),
            radius * np.sin(angle),
            0.0,
        ])
        circles[i].move_to(current_pos)
        vectors[i].put_start_and_end_on(current_pos, next_pos)
        current_pos = next_pos

    epicycle_group = VGroup(circles, vectors)
    epicycle_group.add_updater(update_epicycles)
    update_epicycles(epicycle_group)  

    tip_dot = Dot(radius=0.03, color=YELLOW)
    tip_dot.add_updater(lambda d: d.move_to(vectors[-1].get_end()))

    drawn_path = TracedPath(
        tip_dot.get_center,
        stroke_color=YELLOW,
        stroke_width=2.5,
    )

    self.add(epicycle_group, tip_dot, drawn_path)

    self.play(
        t_tracker.animate.set_value(1),
        run_time=12,
        rate_func=linear,
    )
    self.wait(2)