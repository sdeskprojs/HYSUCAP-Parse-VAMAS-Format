from collections import OrderedDict

import logging
logger = logging.getLogger('VAMASConvertor')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def extract_vamas_data_and_meta(block):
    jHeader = dict()
    jInfo = dict()
    column_names = []; units = []
    for key in list(block.keys())[:-1]: # except last key which is the numerical data
        jHeader[key] = block[key]

    if block['scan_mode'] == 'REGULAR':
        columnX = block['abscissa_label']
        column_names.append(columnX) # if a column X was created, add its label
        units.append(block['abscissa_units'])
        
    column_names += (block['corresponding_variables'])  
    units.append(block['corresponding_variables_units']) 
    data = block['data_values']

    jInfo['columnNames'] = column_names
    jInfo['columnX'] = columnX
    jInfo['units'] = units
    return jHeader, jInfo, data


def isVAMAS(datafile):
    datafile.seek(0)

    # look for VAMAS format signature
    for line in datafile:
        if line.strip() == 'VAMAS Surface Chemical Analysis Standard Data Transfer Format 1988 May 4':
            return True
    else:
        return False


def parseVAMAS(datafile):

    # try:
    datafile.seek(0)

    file_iter = iter(datafile)

    def readline():
        return next(file_iter)

    # look for VAMAS format signature

    for first_line in file_iter:
        if first_line.strip() == 'VAMAS Surface Chemical Analysis Standard Data Transfer Format 1988 May 4':
            break
    else:
        return None


    data = OrderedDict()

    header = OrderedDict()
    header['format_identifier'] = first_line.strip()
    header['institution_identifier'] = readline().strip()
    header['instrument_model_identifier'] = readline().strip()
    header['operator_identifier'] = readline().strip()
    header['experiment_identifier'] = readline().strip()


    comment_length = int(readline().strip())
    if comment_length:
        comment = "\n"
        for i in range(comment_length):
            comment += '\t' + readline()
        header['comment'] = comment

    experiment_mode = readline().strip().upper()
    header['experiment_mode'] = experiment_mode

    scan_mode = readline().strip()
    header['scan_mode'] = scan_mode

    if experiment_mode in ['MAP','MAPDP','NORM','SDP']:
        header['number_of_spectral_regions'] = int(readline().strip())

    if experiment_mode in ['MAP', 'MAPDP']:
        header['number_of_analysis_positions'] = int(readline().strip())
        header['number_of_discrete_x_coordinates_available_in_full_map'] = int(readline().strip())
        header['number_of_discrete_y_coordinates_available_in_full_map'] = int(readline().strip())

    experimental_variables_count = int(readline().strip())

    experimental_variables = list()
    units = list()
    for i in range(experimental_variables_count):
        label = readline().strip()
        unit = readline().strip()
        units.append(unit)
        experimental_variables.append('{} ({})'.format(label,unit))
    header['experimental_variables'] = experimental_variables
    header['experimental_variables_units'] = units


    number_of_entries_in_parameter_inclusion_or_exclusion_list = int(readline().strip())
    if number_of_entries_in_parameter_inclusion_or_exclusion_list:
        parameter_list = []
        for i in range(abs(number_of_entries_in_parameter_inclusion_or_exclusion_list)):
            parameter_list.append(int(readline().strip()))
        # if number_of_entries_in_parameter_inclusion_or_exclusion_list < 0:
        #     header['parameter_exclusion_list'] = parameter_list
        # else:
        #     header['parameter_inclusion_list'] = parameter_list

    number_of_manually_entered_items_in_block = int(readline().strip())

    if number_of_manually_entered_items_in_block:
        manually_entered_items = list()
        for i in range(number_of_manually_entered_items_in_block):
            manually_entered_items.append(int(readline().strip()))
        header['manually_entered_items'] = manually_entered_items

    number_of_future_upgrade_experiment_entries = int(readline().strip())

    number_of_future_upgrade_block_entries = int(readline().strip())

    if number_of_future_upgrade_experiment_entries:
        future_upgrade_experiment_entries = list()
        for i in range(number_of_future_upgrade_experiment_entries):
            future_upgrade_experiment_entries.append(readline().strip())
        header['future_upgrade_experiment_entries'] = future_upgrade_experiment_entries

    number_of_blocks = int(readline().strip())

    data['header'] = header

    ## Blocks

    data['blocks'] = list()

    for block_idx in range(number_of_blocks):
        block = OrderedDict()
        block['scan_mode'] = header['scan_mode']
        block['block_identifier']= readline().strip()
        block['sample_identifier']= readline().strip()

        if block_idx == 0 or number_of_entries_in_parameter_inclusion_or_exclusion_list == 0:
            params_available = range(1, 41)
        elif number_of_entries_in_parameter_inclusion_or_exclusion_list < 0:
            params_available = set(range(1,41)) - set(parameter_list)
        elif number_of_entries_in_parameter_inclusion_or_exclusion_list > 0:
            params_available = set(parameter_list)


        # begin numbered parameters in format specification
        # 1
        if 1 in params_available:
            year =  readline().strip()
            if year == '-1':
                year = ''

        # 2
        if 2 in params_available:
            month =  readline().strip()
            if month == '-1':
                month = ''
            else:
                month = '-' + month

        # 3
        if 3 in params_available:
            day =  readline().strip()
            if day == '-1':
                day = ''
            else:
                day = '-' + day

        # 4
        if 4 in params_available:
            hours =  readline().strip()
            if hours == '-1':
                hours = ''
            else:
                hours = ' ' + hours

        # 5
        if 5 in params_available:
            minutes =  readline().strip()
            if minutes == '-1':
                minutes = ''
            else:
                minutes = ':' + minutes

        # 6
        if 6 in params_available:
            seconds =  readline().strip()
            if seconds == '-1':
                seconds = ''
            else:
                seconds = ':' + seconds

        # 7
        if 7  in params_available:
            number_of_hours_in_advance_of_greenwich_mean_time = int(readline().strip())
            if number_of_hours_in_advance_of_greenwich_mean_time < 0:
                GMT = ' GMT {}'.format(number_of_hours_in_advance_of_greenwich_mean_time)
            else:
                GMT = ' GMT +{}'.format(number_of_hours_in_advance_of_greenwich_mean_time)


        date = ""
        try:
            date += year
        except NameError:
            pass
        try:
            date += month
        except NameError:
            pass
        try:
            date += day
        except NameError:
            pass
        try:
            date += hours
        except NameError:
            pass
        try:
            date += minutes
        except NameError:
            pass
        try:
            date += seconds
        except NameError:
            pass
        try:
            date += GMT
        except NameError:
            pass

        block['date'] = date

        # 8
        if 8 in params_available:
            block_comment_count = int(readline().strip())
            if block_comment_count:
                block_comment = "\n"
                for i in range(block_comment_count):
                    block_comment += '\t' + readline()
                block['block_comment']= block_comment

        # 9
        if 9 in params_available:
            technique = readline().strip().upper()
            block['technique']= technique

        # 10
        if 10 in params_available:
            if experiment_mode in ['MAP','MAPDP']:
                block['x_coordinate']= int(readline().strip())
                block['y_coordinate']= int(readline().strip())

        # 11
        if 11 in params_available:
            values = list()
            for i, v in enumerate(experimental_variables):
                # values.append(('{} ({})'.format(*v), float(readline().strip())))
                values.append('{}={}'.format(v, float(readline().strip())))
            block['experimental_variables']= values


        # 12
        if 12 in params_available:
            block['analysis_source_label']= readline().strip()

        # 13
        if 13 in params_available:
            if experiment_mode in ['MAPDP','MAPSVDP','SDP','SVDP'] or \
                    technique in ['FABMS','FABMS energy spec','ISS','SIMS','SIMS energy spec','SNMS','SNMS energy spec']:
                block['sputtering_ion_or_atomic_number']= readline().strip()
                block['number_of_atoms_in_sputtering_ion_or_atom_particle']= int(readline().strip())
                block['sputtering_ion_or_atom_charge_sign_and_number']= int(readline().strip())

        # 14
        try:
            if 14 in params_available:
                block['analysis_source_characteristic_energy']= float(readline().strip())
        except ValueError:
            pass

        # 15
        if 15 in params_available:
            block['analysis_source_strength']= float(readline().strip())

        # 16
        if 16 in params_available:
            block['analysis_source_beam_width_x']= float(readline().strip())
            block['analysis_source_beam_width_y']= float(readline().strip())

        # 17
        if 17 in params_available and experiment_mode in ['MAP','MAPDP','MAPSV','MAPSVDP','SEM']:
            block['field_of_view_x']= float(readline().strip())
            block['field_of_view_y']= float(readline().strip())

        # 18
        if 18 in params_available and experiment_mode in ['MAPSV','MAPSVDP','SEM']:
            block['first_linescan_start_x_coordinate']= int(readline().strip())
            block['first_linescan_start_y_coordinate']= int(readline().strip())
            block['first_linescan_finish_x_coordinate']= int(readline().strip())
            block['first_linescan_finish_y_coordinate']= int(readline().strip())
            block['last_linescan_finish_x_coordinate']= int(readline().strip())
            block['last_linescan_finish_y_coordinate']= int(readline().strip())

        # 19
        if 19 in params_available:
            block['analysis_source_polar_angle_of_incidence']= float(readline().strip())

        # 20
        if 20 in params_available:
            block['analysis_source_azimuth']= float(readline().strip())

        # 21
        if 21 in params_available:
            block['analyser_mode']= readline().strip()

        # 22
        try:
            if 22 in params_available:
                block['analyser_pass_energy_of_retard_ratio_or_mass_resolution']= float(readline().strip())
        except:
            pass
        # 23
        if 23 in params_available:
            if technique == 'AES DIFF':
                block['differential_width']= float(readline().strip())

        # 24
        if 24 in params_available:
            block['magnification_of_analyser_transfer_lens']= float(readline().strip())

        # 25
        if 25 in params_available:
            block['analyser_work_function_or_acceptance_energy_of_atom_or_ion']= float(readline().strip())

        # 26
        if 26 in params_available:
            block['target_bias']= float(readline().strip())

        # 27
        if 27 in params_available:
            block['analysis_width_x']= float(readline().strip())
            block['analysis_width_y']= float(readline().strip())

        # 28
        if 28 in params_available:
            block['analyser_axis_take_off_polar_angle']= float(readline().strip())
            block['analyser_axis_take_off_azimuth']= float(readline().strip())

        # 29
        if 29 in params_available:
            block['species_label']= readline().strip()

        # 30
        try:
            if 30 in params_available:
                block['transition_or_charge_state_label']= readline().strip()
                block['charge_of_detected_particle']= int(readline().strip())
        except:
            pass

        # 31
        try:
            if 31 in params_available and scan_mode == 'REGULAR':
                block['abscissa_label']= readline().strip()
                block['abscissa_units']= readline().strip()
                block['abscissa_start']= float(readline().strip())
                block['abscissa_increment']= float(readline().strip())
        except:
            pass


        # 32
        if 32 in params_available:
            number_of_variables = int(float(readline().strip()))
            variables_in_columns = list()
            units =list()
            for i in range(number_of_variables):
                label = readline().strip()
                unit = readline().strip()
                units.append(unit)
                # variables_in_columns.append((label, unit))
                variables_in_columns.append('{} ({})'.format(label, unit))
            block['corresponding_variables']= variables_in_columns
            block['corresponding_variables_units']= units

        # 33
        if 33 in params_available:
            block['signal_mode']= readline().strip()

        # 34
        if 34 in params_available:
            block['signal_collection_time']= float(readline().strip())

        # 35
        if 35 in params_available:
            block['number_of_scans_to_compile_this_block']= int(readline().strip())

        # 36
        if 36 in params_available:
            block['signal_time_correction']= float(readline().strip())

        # 37
        if 37 in params_available and technique in ['AES DIFF','AES DIR','EDX','ELS','UPS','XPS','XRF'] and \
                experiment_mode in ['MAPDP','MAPSVDP','SDP','SDPSV']:
            block['sputtering_source_energy']= float(readline().strip())
            block['sputtering_source_beam_current']= float(readline().strip())
            block['sputtering_source_width_x']= float(readline().strip())
            block['sputtering_source_width_y']= float(readline().strip())
            block['sputtering_source_polar_angle_of_incidence']= float(readline().strip())
            block['sputtering_source_azimuth']= float(readline().strip())
            block['sputtering_mode']= readline().strip()

        # 38
        if 38 in params_available:
            block['sample_normal_polar_angle_of_tilt']= float(readline().strip())
            block['sample_normal_tilt_azimuth']= float(readline().strip())

        # 39
        if 39 in params_available:
            block['sample_rotation_angle']= float(readline().strip())

        # 40
        if 40 in params_available:
            number_of_additional_numerical_parameters = int(readline().strip())
            numerical_parameters = []
            for i in range(number_of_additional_numerical_parameters):
                label = readline().strip()
                unit = readline().strip()
                try:
                    str_value = readline().strip()
                    value = float(str_value)
                except:
                    value = str_value
                # numerical_parameters.append((label, unit, value))
                numerical_parameters.append('{} ({})={}'.format(label, unit, value))
            block['additional_numerical_parameters']= numerical_parameters

        # end numbered parameters

        future_upgrade_block_entries = list()
        for i in range(number_of_future_upgrade_block_entries):
            future_upgrade_block_entries.append(readline().strip())
        block['future_upgrade_block_entries']= future_upgrade_block_entries

        number_data_points_in_block = int(readline().strip())
        number_of_data_points_in_each_variable = number_data_points_in_block//number_of_variables

        variable_ranges = list()
        for i in range(number_of_variables):
            minimum_ordinate_value = float(readline().strip())
            maximum_ordinate_value = float(readline().strip())
            # variable_ranges.append((minimum_ordinate_value, maximum_ordinate_value))
            variable_ranges.append('{}: [{}, {}]'.format(variables_in_columns[i],minimum_ordinate_value,
                                                        maximum_ordinate_value))
        block['variables_ranges']= variable_ranges


        numerical_data = list()
        for row in range(number_of_data_points_in_each_variable):
            line = list()
            if scan_mode == 'REGULAR':  # create a X column
                line.append(block['abscissa_start'] + row*block['abscissa_increment'])
            for column in range(number_of_variables):
                line.append(float(readline().strip()))
            numerical_data.append(line)

        block['data_values'] = numerical_data

        data['blocks'].append(block)

    return data


