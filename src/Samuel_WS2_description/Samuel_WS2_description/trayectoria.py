"""Draw a group digit using odometry feedback; publish the measured path."""
import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Odometry, Path


# Coordinates on a 1 x 2 metre writing plane. Repeated edges keep strokes connected.
DIGITS = {
    0: [(0, 0), (1, 0), (1, 2), (0, 2), (0, 0)],
    1: [(0, 1.5), (.5, 2), (.5, 0)],
    2: [(0, 2), (1, 2), (1, 1), (0, 1), (0, 0), (1, 0)],
    3: [(0, 2), (1, 2), (1, 1), (0, 1), (1, 1), (1, 0), (0, 0)],
    4: [(0, 2), (0, 1), (1, 1), (1, 2), (1, 0)],
    5: [(1, 2), (0, 2), (0, 1), (1, 1), (1, 0), (0, 0)],
    6: [(1, 2), (0, 2), (0, 0), (1, 0), (1, 1), (0, 1)],
    7: [(0, 2), (1, 2), (0, 0)],
    8: [(0, 1), (0, 2), (1, 2), (1, 0), (0, 0), (0, 1), (1, 1)],
    9: [(1, 1), (0, 1), (0, 2), (1, 2), (1, 0), (0, 0)],
}


def steering(x, y, yaw, target):
    dx, dy = target[0] - x, target[1] - y
    distance = math.hypot(dx, dy)
    error = math.atan2(math.sin(math.atan2(dy, dx) - yaw),
                       math.cos(math.atan2(dy, dx) - yaw))
    if distance < .025:
        return 0., 0., True
    angular = max(-.65, min(.65, 2.0 * error))
    linear = min(.12, .65 * distance) if abs(error) < .12 else 0.
    return linear, angular, False


class Trajectory(Node):
    def __init__(self):
        super().__init__('trayectoria_ws2')
        self.declare_parameter('grupo', -1)
        group = self.get_parameter('grupo').value
        if not isinstance(group, int) or not 1 <= group <= 22:
            raise ValueError('Indica tu grupo (1 a 22): --ros-args -p grupo:=17')
        self.digit = group % 10
        self.points = None
        self.index = 1
        self.pose = None
        self.last_odom = time.monotonic()
        self.done = False
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.path_pub = self.create_publisher(Path, '/trayectoria', qos)
        self.path = Path()
        self.path.header.frame_id = 'odom'
        self.create_subscription(Odometry, '/odom', self.odometry, 10)
        self.create_timer(.05, self.control)
        self.get_logger().info(f'Grupo {group}: dígito {self.digit}. Esperando odometría...')

    def odometry(self, msg):
        self.last_odom = time.monotonic()
        p, q = msg.pose.pose.position, msg.pose.pose.orientation
        yaw = math.atan2(2 * (q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
        self.pose = (p.x, p.y, yaw)
        if self.points is None:
            raw = DIGITS[self.digit]
            self.points = [(p.x + x - raw[0][0], p.y + y - raw[0][1]) for x, y in raw]
        if not self.path.poses or math.hypot(p.x-self.path.poses[-1].pose.position.x,
                                           p.y-self.path.poses[-1].pose.position.y) >= .01:
            pose = PoseStamped()
            pose.header = msg.header
            pose.pose = msg.pose.pose
            self.path.poses.append(pose)
        self.path.header.stamp = msg.header.stamp
        self.path_pub.publish(self.path)

    def control(self):
        cmd = Twist()
        if self.pose is not None and not self.done and time.monotonic()-self.last_odom < 1.0:
            v, w, reached = steering(*self.pose, self.points[self.index])
            if reached:
                self.index += 1
                if self.index == len(self.points):
                    self.done = True
                    self.get_logger().info('Trayectoria terminada. Robot detenido.')
            else:
                cmd.linear.x, cmd.angular.z = v, w
        self.pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = Trajectory()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            if rclpy.ok():
                node.pub.publish(Twist())
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
