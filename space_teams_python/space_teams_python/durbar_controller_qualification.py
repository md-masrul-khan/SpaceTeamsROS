#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from space_teams_definitions.srv import String, Float
import time


class DurbarController(Node):
    def __init__(self):
        super().__init__('durbar_controller')

        # Service clients
        self.cli_log = self.create_client(String, '/log_message')
        self.cli_accel = self.create_client(Float, '/Accelerator')
        self.cli_steer = self.create_client(Float, '/Steer')
        self.cli_reverse = self.create_client(Float, '/Reverse')
        self.cli_brake = self.create_client(Float, '/Brake')

        # Wait for all services
        for cli, name in [
            (self.cli_log, '/log_message'),
            (self.cli_accel, '/Accelerator'),
            (self.cli_steer, '/Steer'),
            (self.cli_reverse, '/Reverse'),
            (self.cli_brake, '/Brake'),
        ]:
            while not cli.wait_for_service(timeout_sec=2.0):
                self.get_logger().warn(f'Waiting for {name} service...')

        self.run_sequence()

    def call_service(self, client, req):
        """Helper to send request and wait for result."""
        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        if future.result() is not None:
            return future.result()
        else:
            self.get_logger().error('Service call failed')
            return None

    def run_sequence(self):
        time.sleep(5)
        self.get_logger().info('Sending "Hello" to /log_message')
        req_log = String.Request()
        req_log.data = "Hello"
        self.call_service(self.cli_log, req_log)


        req_accel = Float.Request()
        req_brake = Float.Request()
        req_steer = Float.Request()
        req_reverse = Float.Request()

        #start
        req_accel.data = 0.0
        req_brake.data = 0.0
        req_reverse.data = 0.0
        req_steer.data = 0.0
        self.call_service(self.cli_accel, req_accel)
        self.call_service(self.cli_reverse, req_reverse)
        self.call_service(self.cli_brake, req_brake)
        self.call_service(self.cli_steer, req_steer)
        # ---- Move forward ----
        self.get_logger().info('Moving forward')
        req_accel.data = 1.0
        self.call_service(self.cli_accel, req_accel)
        time.sleep(5)
        req_accel.data = 0.0
        self.call_service(self.cli_accel, req_accel)

        # ---- Steer ----
        self.get_logger().info('Steering right')
        req_steer.data = 0.8    # positive = right, negative = left
        self.call_service(self.cli_steer, req_steer)
        time.sleep(3)
        req_steer.data = 0.0    # positive = right, negative = left
        self.call_service(self.cli_steer, req_steer)
        time.sleep(0.5)

        # ---- Reverse ----
        self.get_logger().info('Reversing')
        req_reverse.data = 1.0
        self.call_service(self.cli_reverse, req_reverse)
        time.sleep(3.0)
        req_reverse.data = 0.0
        self.call_service(self.cli_reverse, req_reverse)
        time.sleep(2.0)

        # ---- Brake ----
        self.get_logger().info('Braking')
        req_brake.data = 1.0
        self.call_service(self.cli_brake, req_brake)
        time.sleep(2)
        req_brake.data = 0.0
        self.call_service(self.cli_brake, req_brake)

        self.get_logger().info('Sequence complete.')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = DurbarController()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
