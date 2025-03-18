import random

def signal_map(in_port, out_port):

    in_ports = in_port.copy()
    out_ports = out_port.copy()
    
    random.shuffle(in_ports)
    
    mapping = []
    
    for out in out_ports:
        if in_ports:
            in_p = in_ports.pop(0)
            mapping.append((in_p, out))
    
    while in_ports:
        out_p = random.choice(out_ports)
        in_p = in_ports.pop(0)
        mapping.append((in_p, out_p))
    
    return mapping

def group_ports(in_port, out_port):
    mapping = signal_map(in_port, out_port)
    
    out_to_in = {}
    for in_p, out_p in mapping:
        out_name = out_p['name']
        if out_name not in out_to_in:
            out_to_in[out_name] = []
        out_to_in[out_name].append(in_p)
    
    out_port_names = list(out_to_in.keys())
    random.shuffle(out_port_names)
    
    split_point = random.randint(1, max(1, len(out_port_names) - 1))
    
    arbiter_out_names = out_port_names[:split_point]
    fsm_out_names = out_port_names[split_point:]
    
    in_port_arbiter = []
    in_port_fsm = []
    out_port_arbiter = []
    out_port_fsm = []
    
    for out_name in arbiter_out_names:
        out_port_obj = next(out_p for _, out_p in mapping if out_p['name'] == out_name)
        out_port_arbiter.append(out_port_obj)
        in_port_arbiter.extend(out_to_in[out_name])
    
    for out_name in fsm_out_names:
        out_port_obj = next(out_p for _, out_p in mapping if out_p['name'] == out_name)
        out_port_fsm.append(out_port_obj)
        in_port_fsm.extend(out_to_in[out_name])
    
    return in_port_arbiter, in_port_fsm, out_port_arbiter, out_port_fsm

