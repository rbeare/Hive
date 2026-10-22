import eventmanager
import model
import view
import controller

def run():
    event_manager = eventmanager.HiveEventManager()
    h_model = model.HiveModel(event_manager)
    h_controller = controller.HiveController(event_manager, h_model)
    h_view = view.HiveView(event_manager, h_model)
    h_model.run()

if __name__ == '__main__':
    run()